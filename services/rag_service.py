"""
services/rag_service.py — RAG Pipeline (PDF → FAISS → Search)
==============================================================
Extracted and improved from the GenAI Project's app.py.

Original issues fixed:
  • Global mutable state (vector_db, processed_files) → now returns objects
  • Bare except clauses → specific exception handling
  • No logging → full logging added

Workflow:
  1. Load PDFs with PyPDFLoader
  2. Validate each PDF is a legal document
  3. Split into chunks with RecursiveCharacterTextSplitter
  4. Generate embeddings with HuggingFace MiniLM
  5. Store in FAISS vector database
  6. Query with similarity_search()
"""

import logging
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_community.vectorstores import FAISS

from config import (
    EMBEDDING_MODEL_NAME,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    RAG_TOP_K,
)
from utils.validators import is_legal_document

logger = logging.getLogger(__name__)

# ── Embeddings Model (initialized once) ─────────────────────
# From GenAI Project — sentence-transformers/all-MiniLM-L6-v2
_embeddings = None


def _get_embeddings() -> FastEmbedEmbeddings:
    """Lazy-initialize the embedding model (downloads on first use)."""
    global _embeddings
    if _embeddings is None:
        logger.info("⏳ Loading embedding model: BAAI/bge-small-en-v1.5 ...")
        _embeddings = FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")
        logger.info("✅ Embedding model loaded")
    return _embeddings


def process_pdfs(files: list) -> tuple:
    """
    Process multiple PDF files into a FAISS vector store.

    This is the refactored version of GenAI's process_multiple_pdfs().
    Key improvement: no global state — returns the database object.

    Args:
        files: List of Gradio File objects (each has a .name attribute).

    Returns:
        tuple: (FAISS_db_or_None, status_message_string)
    """
    all_chunks = []
    valid_files = []

    try:
        for file in files:
            file_path = file.name if hasattr(file, "name") else str(file)
            logger.info("📄 Processing PDF: %s", file_path)

            # Step 1: Load PDF pages
            loader = PyPDFLoader(file_path)
            documents = loader.load()

            if not documents:
                logger.warning("⚠️  Empty PDF skipped: %s", file_path)
                continue

            # Step 2: Validate it's a legal document
            if not is_legal_document(documents):
                logger.warning("⚠️  Not a legal document, skipping: %s", file_path)
                continue

            # Step 3: Split into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=CHUNK_SIZE,
                chunk_overlap=CHUNK_OVERLAP,
            )
            chunks = text_splitter.split_documents(documents)

            # Tag each chunk with its source file
            for chunk in chunks:
                chunk.metadata["source"] = file_path

            all_chunks.extend(chunks)
            valid_files.append(file_path)
            logger.info("✅ %s → %d chunks", file_path, len(chunks))

        # Step 4: Build FAISS index
        if not all_chunks:
            return None, "⚠️ No valid legal PDFs found in the uploaded files."

        embeddings = _get_embeddings()
        db = FAISS.from_documents(all_chunks, embeddings)

        msg = f"✅ Processed {len(valid_files)} legal PDF(s) — {len(all_chunks)} chunks indexed."
        logger.info(msg)
        return db, msg

    except Exception as exc:
        error_msg = f"❌ Error processing PDFs: {str(exc)}"
        logger.error(error_msg, exc_info=True)
        return None, error_msg


def query_documents(vector_db: FAISS, question: str, k: int = RAG_TOP_K) -> str:
    """
    Retrieve the most relevant chunks from the vector store.

    This replaces the inline vector_db.similarity_search() call
    in the GenAI project's chat_func().

    Args:
        vector_db: A FAISS vector store instance.
        question:  The user's question.
        k:         Number of top results to return.

    Returns:
        Combined text of the top-k matching chunks, or empty string.
    """
    results = vector_db.similarity_search(question, k=k)

    if not results:
        logger.info("No relevant chunks found for: %s", question[:80])
        return ""

    context = "\n\n".join(doc.page_content for doc in results)
    logger.info("Found %d relevant chunks (%d chars)", len(results), len(context))
    return context

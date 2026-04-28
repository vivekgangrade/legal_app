"""
app.py — Legal AI Platform (Production-Ready)
===============================================
Main entry point that combines BOTH original projects into a single
tabbed Gradio interface with production features:

  Tab 1: 📄 Document Q&A    (from GenAI Project)
  Tab 2: 🔍 Legal Research   (from Agentic AI Project)

Production features:
  • Health check endpoint (/health, /ready)
  • Optional basic auth in production mode
  • Request logging
  • Graceful error handling
  • Environment-based configuration

How to run:
  Development:  python app.py
  Production:   gunicorn app:app --bind 0.0.0.0:10000
  Docker:       docker-compose up
"""

import logging
import gradio as gr

from config import PORT, IS_PRODUCTION, GRADIO_AUTH_USER, GRADIO_AUTH_PASS
from services.rag_service import process_pdfs, query_documents
from services.llm_service import get_rag_answer
from services.research_service import generate_legal_report
from services.pdf_service import generate_pdf
from utils.validators import is_legal_query

logger = logging.getLogger(__name__)

# =====================================================================
#  STATE MANAGEMENT
# =====================================================================
_session = {
    "vector_db": None,
    "processed_files": set(),
}


# =====================================================================
#  TAB 1: DOCUMENT Q&A  (from GenAI Project)
# =====================================================================
def document_qa(message: str, history: list, files: list) -> str:
    """
    Chat handler for the Document Q&A tab.
    Flow: upload PDFs → process into FAISS → answer questions from context.
    """
    if not files:
        return "📎 Please upload at least one legal PDF to get started."

    try:
        file_names = set(f.name if hasattr(f, "name") else str(f) for f in files)

        if file_names != _session["processed_files"] or _session["vector_db"] is None:
            logger.info("📄 New files detected — processing PDFs...")
            db, status = process_pdfs(files)

            if db is None:
                _session["vector_db"] = None
                _session["processed_files"] = set()
                return status

            _session["vector_db"] = db
            _session["processed_files"] = file_names
            logger.info(status)

        if _session["vector_db"] is None:
            return "⚠️ No valid legal documents available. Please upload legal PDFs."

        context = query_documents(_session["vector_db"], message)

        if not context:
            return "🔍 No relevant information found in the uploaded documents."

        answer = get_rag_answer(context, message)
        return answer

    except ValueError as exc:
        return f"⚙️ Configuration Error: {str(exc)}"
    except Exception as exc:
        logger.error("Document Q&A error: %s", exc, exc_info=True)
        return f"❌ Error: {str(exc)}"


# =====================================================================
#  TAB 2: LEGAL RESEARCH  (from Agentic AI Project)
# =====================================================================
def legal_research(query: str) -> tuple:
    """
    Handler for the Legal Research tab.
    Flow: validate query → web search → LLM report → PDF download.
    """
    if not query or not query.strip():
        return "⚠️ Please enter a legal query.", None

    try:
        if not is_legal_query(query):
            return (
                "❌ Only legal queries are supported.\n\n"
                "**Try examples like:**\n"
                "- Cybercrime laws in India\n"
                "- IT Act 2000\n"
                "- Data privacy laws\n"
                "- Rights of accused in criminal cases\n"
                "- Intellectual property rights",
                None,
            )

        report, sources = generate_legal_report(query)

        if not sources:
            return report, None

        pdf_path = generate_pdf(report, query)
        return report, pdf_path

    except ValueError as exc:
        return f"⚙️ Configuration Error: {str(exc)}", None
    except Exception as exc:
        logger.error("Legal Research error: %s", exc, exc_info=True)
        return f"❌ Error: {str(exc)}", None


# =====================================================================
#  GRADIO UI — TABBED INTERFACE
# =====================================================================
def build_app() -> gr.Blocks:
    """
    Build the merged Gradio application with two tabs.
    Mounts the health check FastAPI app for /health and /ready endpoints.
    """

    with gr.Blocks(
        title="⚖️ Legal AI Platform",
    ) as gradio_app:

        # ── Header ───────────────────────────────────────────
        gr.Markdown(
            """
            # ⚖️ Legal AI Platform
            ### Unified Legal Assistant — Document Q&A + Web Research

            *Powered by Groq LLaMA 3.1 • FAISS • Tavily Search*
            """
        )

        with gr.Tabs():

            # ── TAB 1: Document Q&A (from GenAI) ────────────
            with gr.TabItem("📄 Document Q&A"):
                gr.Markdown(
                    """
                    **Upload legal PDFs** and ask questions about their content.
                    The AI answers using only the information in your documents (RAG).
                    """
                )

                doc_chat = gr.ChatInterface(
                    fn=document_qa,
                    additional_inputs=[
                        gr.File(
                            label="Upload Legal PDFs",
                            file_types=[".pdf"],
                            file_count="multiple",
                        )
                    ],
                    examples=[
                        ["Summarize the key terms of this agreement"],
                        ["What are the liability clauses?"],
                        ["What jurisdiction does this contract fall under?"],
                        ["List all obligations of the parties"],
                    ],
                )

            # ── TAB 2: Legal Research (from Agentic AI) ─────
            with gr.TabItem("🔍 Legal Research"):
                gr.Markdown(
                    """
                    **Enter a legal topic** to get a professionally researched report
                    with real-time web sources. Download the report as PDF.
                    """
                )

                query_input = gr.Textbox(
                    label="Enter Legal Query",
                    placeholder="e.g. What are cybercrime laws in India?",
                    lines=2,
                )

                with gr.Row():
                    research_btn = gr.Button("🔍 Research", variant="primary")
                    clear_btn = gr.Button("🗑️ Clear")

                report_output = gr.Markdown(label="Research Report")
                pdf_output = gr.File(label="📥 Download PDF Report")

                research_btn.click(
                    fn=legal_research,
                    inputs=query_input,
                    outputs=[report_output, pdf_output],
                    show_progress="full",
                )
                clear_btn.click(
                    fn=lambda: ("", "", None),
                    inputs=None,
                    outputs=[query_input, report_output, pdf_output],
                )

                gr.Examples(
                    examples=[
                        "What are data privacy laws in India?",
                        "Is web scraping legal in India?",
                        "What are penalties for cybercrime in India?",
                        "Explain IT Act 2000 in India",
                        "Rights of an arrested person in India",
                    ],
                    inputs=[query_input],
                )

        # ── Footer ───────────────────────────────────────────
        gr.Markdown(
            """
            ---
            *Built by merging [GenAI Project](https://github.com/Jogendar-Bairagi/GenAI-Project)
            (RAG) + [Agentic AI](https://github.com/Jogendar-Bairagi/Agentic-AI)
            (Web Research) into one platform.*
            """
        )

    return gradio_app


# =====================================================================
#  ENTRY POINT
# =====================================================================

if __name__ == "__main__":
    logger.info(
        "Starting Legal AI Platform on port %d (env=%s) ...",
        PORT,
        "production" if IS_PRODUCTION else "development",
    )

    # Build the Gradio app
    _gradio_app = build_app()

    # ── Build launch kwargs ──────────────────────────────────
    launch_kwargs = {
        "server_name": "0.0.0.0",
        "server_port": PORT,
        "theme": gr.themes.Soft(),
    }

    # Enable basic auth in production if credentials are set
    if IS_PRODUCTION and GRADIO_AUTH_USER and GRADIO_AUTH_PASS:
        launch_kwargs["auth"] = (GRADIO_AUTH_USER, GRADIO_AUTH_PASS)
        logger.info("Basic auth enabled for production")

    # Launch Gradio — this creates the internal FastAPI app
    gradio_app_instance, local_url, share_url = _gradio_app.launch(
        **launch_kwargs,
        prevent_thread_lock=True,
    )

    # ── Mount health check routes AFTER launch ───────────────
    # Gradio 6 creates its FastAPI app only during launch(),
    # so we add our routes after that.
    from health import health_router
    _gradio_app.app.include_router(health_router)

    logger.info("Health endpoints registered: /health, /ready")

    # Block the main thread (like Gradio normally does)
    _gradio_app.block_thread()


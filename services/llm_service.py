"""
services/llm_service.py — Shared LLM Client
=============================================
Provides a SINGLE LLM instance used by both the RAG pipeline
(from GenAI Project) and the research agent (from Agentic AI).

Changes from originals:
  • GenAI used the raw `groq` SDK → replaced with LangChain ChatGroq
  • Agentic AI initialized ChatGroq TWICE → now one instance
  • Added retry logic for API resilience
  • Added proper logging
"""

import logging
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from config import GROQ_API_KEY, LLM_MODEL_NAME, LLM_TEMPERATURE, API_TIMEOUT
from utils.retry import retry_on_failure

logger = logging.getLogger(__name__)

# ── Single LLM Instance ─────────────────────────────────────
# Created once at import time; reused by all callers.
# This replaces BOTH the raw Groq client (GenAI) and the
# duplicate ChatGroq instances (Agentic AI).
_llm = None


def _get_llm() -> ChatGroq:
    """Lazy-initialize the LLM so we fail gracefully if key is missing."""
    global _llm
    if _llm is None:
        if not GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY is not set. "
                "Please add it to your .env file or system environment."
            )
        _llm = ChatGroq(
            model_name=LLM_MODEL_NAME,
            temperature=LLM_TEMPERATURE,
            groq_api_key=GROQ_API_KEY,
            request_timeout=API_TIMEOUT,
        )
        logger.info("✅ LLM initialized: %s", LLM_MODEL_NAME)
    return _llm


# ── RAG Q&A (from GenAI Project) ────────────────────────────
@retry_on_failure(max_retries=3, backoff_factor=2.0)
def get_rag_answer(context: str, question: str) -> str:
    """
    Answer a question using ONLY the provided document context.

    This replaces the raw Groq API call in the GenAI project's chat_func().
    The system prompt forces the LLM to stay grounded in the context.

    Args:
        context:  Relevant text chunks retrieved from FAISS.
        question: The user's question.

    Returns:
        The LLM's answer string.
    """
    logger.info("Generating RAG answer for: %s", question[:80])

    llm = _get_llm()
    messages = [
        SystemMessage(
            content=(
                "You are a Legal AI Assistant. "
                "Answer the user's question ONLY from the context provided below. "
                "If the answer is not in the context, say so clearly.\n\n"
                f"Context:\n{context}"
            )
        ),
        HumanMessage(content=question),
    ]

    response = llm.invoke(messages)
    return response.content


# ── Structured Legal Report (from Agentic AI) ───────────────
@retry_on_failure(max_retries=3, backoff_factor=2.0)
def get_research_report(context: str, query: str) -> str:
    """
    Generate a structured legal research report from web-sourced context.

    This replaces the inline prompt + llm.invoke() in the Agentic AI
    project's legal_agent() function.

    Args:
        context: Combined text from Tavily search results.
        query:   The user's legal research query.

    Returns:
        Formatted report string (without sources — those are appended later).
    """
    logger.info("Generating research report for: %s", query[:80])

    llm = _get_llm()

    # This prompt is from the Agentic AI project, kept as-is for output format.
    prompt = f"""
    You are a professional legal researcher.

    STRICT FORMAT (follow exactly):

    Topic:
    <paragraph>

    Key Laws or Acts:
    1. <law name>: <description>

    Important Points:
    - point
    - point

    Conclusion:
    <short paragraph>

    DO NOT use:
    - ** symbols
    - ### symbols

    Query: {query}

    Context:
    {context}
    """

    response = llm.invoke(prompt)
    return response.content

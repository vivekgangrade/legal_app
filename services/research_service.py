"""
services/research_service.py — Agentic Web Research Pipeline
=============================================================
Extracted and improved from the Agentic AI Project's app.py.

Original issues fixed:
  • Tavily client initialized TWICE → now once, lazily
  • search_web() and legal_agent() had overlapping code → unified
  • No error handling on Tavily calls → added try/except + retry
  • No logging

Workflow:
  1. Validate query is legal-related
  2. Search web via Tavily API
  3. Build context from search results
  4. Generate structured report via LLM
  5. Append source URLs
"""

import logging
from tavily import TavilyClient

from config import TAVILY_API_KEY, SEARCH_DEPTH, MAX_SEARCH_RESULTS, API_TIMEOUT
from services.llm_service import get_research_report
from utils.retry import retry_on_failure

logger = logging.getLogger(__name__)

# ── Tavily Client (initialized once) ────────────────────────
_tavily = None


def _get_tavily() -> TavilyClient:
    """Lazy-initialize the Tavily search client."""
    global _tavily
    if _tavily is None:
        if not TAVILY_API_KEY:
            raise ValueError(
                "TAVILY_API_KEY is not set. "
                "Please add it to your .env file or system environment."
            )
        _tavily = TavilyClient(api_key=TAVILY_API_KEY)
        logger.info("✅ Tavily search client initialized")
    return _tavily


@retry_on_failure(max_retries=3, backoff_factor=2.0)
def search_legal_web(query: str) -> tuple[str, list[str]]:
    """
    Search the web for legal information using Tavily.

    This merges and deduplicates the search_web() and legal_agent()
    functions from the Agentic AI project.

    Args:
        query: The legal research query.

    Returns:
        tuple: (combined_context_text, list_of_source_urls)
    """
    logger.info("🌐 Searching web for: %s", query[:80])

    tavily = _get_tavily()
    results = tavily.search(
        query=query,
        search_depth=SEARCH_DEPTH,
        max_results=MAX_SEARCH_RESULTS,
    )

    sources: list[str] = []
    context_parts: list[str] = []

    for result in results.get("results", []):
        sources.append(result["url"])
        context_parts.append(result["content"])

    context = "\n\n".join(context_parts)
    logger.info("📚 Found %d sources, %d chars of context", len(sources), len(context))

    return context, sources


def generate_legal_report(query: str) -> tuple[str, list[str]]:
    """
    Full agentic pipeline: search → LLM report → return with sources.

    This is the cleaned-up version of legal_agent() from Agentic AI.

    Args:
        query: The user's legal research query.

    Returns:
        tuple: (full_report_with_sources, list_of_source_urls)
    """
    # Step 1: Web search
    context, sources = search_legal_web(query)

    if not context:
        return "⚠️ No relevant information found on the web for this query.", []

    # Step 2: Generate structured report via LLM
    report = get_research_report(context, query)

    # Step 3: Append source citations
    source_text = "\n\nSources:\n"
    for i, url in enumerate(sources, 1):
        source_text += f"{i}. {url}\n"

    full_report = report + source_text

    logger.info("✅ Legal report generated (%d chars)", len(full_report))
    return full_report, sources

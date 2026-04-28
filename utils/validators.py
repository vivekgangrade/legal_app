"""
utils/validators.py — Legal Content Validation
================================================
Merged validation logic from BOTH original projects:

  • GenAI Project  → is_legal_document()  — checks uploaded PDF content
  • Agentic AI     → is_legal_query()     — checks user text queries

Both now share the same LEGAL_KEYWORDS list from config.py.
"""

import logging
from config import LEGAL_KEYWORDS, LEGAL_DOC_MIN_MATCHES

logger = logging.getLogger(__name__)


def is_legal_document(documents: list) -> bool:
    """
    Check whether a list of LangChain Document objects contain legal content.

    This was originally in the GenAI project's app.py. It scans the combined
    text of all pages for legal keywords and returns True if enough matches
    are found (threshold defined in config.LEGAL_DOC_MIN_MATCHES).

    Args:
        documents: List of LangChain Document objects (from PyPDFLoader).

    Returns:
        True if the documents appear to be legal in nature.
    """
    try:
        # Combine all page text into one lowercase string
        full_text = " ".join(doc.page_content.lower() for doc in documents)

        # Count how many legal keywords appear in the text
        match_count = sum(1 for kw in LEGAL_KEYWORDS if kw in full_text)

        is_legal = match_count >= LEGAL_DOC_MIN_MATCHES
        logger.info(
            "Document validation: %d/%d keywords matched → %s",
            match_count,
            LEGAL_DOC_MIN_MATCHES,
            "✅ Legal" if is_legal else "❌ Not legal",
        )
        return is_legal

    except Exception as exc:
        logger.error("Error validating document: %s", exc)
        return False


def is_legal_query(query: str) -> bool:
    """
    Check whether a user's text query is related to legal topics.

    This was originally is_legal_keyword() in the Agentic AI project's app.py.
    It checks if any legal keyword appears anywhere in the query text.

    Args:
        query: The user's search query string.

    Returns:
        True if the query appears to be about a legal topic.
    """
    if not query or not query.strip():
        return False

    query_lower = query.lower()
    is_legal = any(kw in query_lower for kw in LEGAL_KEYWORDS)

    logger.info(
        "Query validation for '%s': %s",
        query[:50],
        "✅ Legal topic" if is_legal else "❌ Not legal topic",
    )
    return is_legal

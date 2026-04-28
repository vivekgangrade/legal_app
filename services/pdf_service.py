"""
services/pdf_service.py — PDF Report Generator
================================================
Extracted and improved from the Agentic AI Project's app.py.

Original issues fixed:
  • Hard-coded output path "/content/legal_report.pdf" (Colab-only) → dynamic
  • Used abandoned `fpdf` library → switched to maintained `fpdf2`
  • No error handling on file write
  • Added proper logging

The generate_pdf() function creates a professionally formatted PDF
with headings, bullet points, numbered lists, and proper text wrapping.
"""

import re
import logging
import uuid
from pathlib import Path
from fpdf import FPDF

from config import OUTPUT_DIR

logger = logging.getLogger(__name__)


def clean_text(text: str) -> str:
    """
    Remove non-Latin-1 characters that FPDF cannot render.

    From Agentic AI Project — kept as-is since FPDF/fpdf2 only
    supports Latin-1 encoding by default.

    Args:
        text: Raw text that may contain Unicode characters.

    Returns:
        Cleaned text safe for FPDF rendering.
    """
    return re.sub(r'[^\x00-\xFF]+', '', text)


def generate_pdf(text: str, title: str) -> str:
    """
    Generate a formatted PDF report from the LLM's output text.

    Extracted from the Agentic AI project's generate_pdf() function.
    Improvements:
      • Dynamic output path (not hard-coded to /content/)
      • Unique filename using UUID to prevent overwrites
      • Better error handling

    Args:
        text:  The full report text (from LLM + sources).
        title: The query/title to display at the top of the PDF.

    Returns:
        Absolute path to the generated PDF file.
    """
    try:
        pdf = FPDF()
        pdf.add_page()

        # ── Title ────────────────────────────────────────────
        pdf.set_font("Arial", "B", 18)
        safe_title = clean_text(title)
        pdf.cell(0, 12, safe_title, ln=True, align="C")
        pdf.ln(5)

        # ── Body ─────────────────────────────────────────────
        text = clean_text(text)
        lines = text.split("\n")

        for line in lines:
            line = line.strip()

            # Skip the "Topic:" label (content follows on next lines)
            if line.lower().startswith("topic"):
                continue

            # Empty line → small vertical space
            if not line:
                pdf.ln(3)
                continue

            # ── SECTION HEADINGS ─────────────────────────────
            if line.lower().startswith("clear explanation"):
                pdf.set_font("Arial", "B", 16)
                pdf.cell(0, 10, "Clear Explanation", ln=True)
                pdf.ln(2)

            elif line.lower().startswith("key laws"):
                pdf.set_font("Arial", "B", 16)
                pdf.cell(0, 10, "Key Laws or Acts", ln=True)
                pdf.ln(2)

            elif line.lower().startswith("important points"):
                pdf.set_font("Arial", "B", 16)
                pdf.cell(0, 10, "Important Points", ln=True)
                pdf.ln(2)

            elif line.lower().startswith("conclusion"):
                pdf.set_font("Arial", "B", 16)
                pdf.cell(0, 10, "Conclusion", ln=True)
                pdf.ln(2)

            elif line.lower().startswith("sources"):
                pdf.set_font("Arial", "B", 16)
                pdf.cell(0, 10, "Sources", ln=True)
                pdf.ln(2)

            # ── NUMBERED LIST (e.g. "1. Something") ──────────
            elif re.match(r'^\d+\.', line):
                pdf.set_font("Arial", size=11)
                number, content = line.split(".", 1)
                number = number.strip() + "."
                content = content.strip()

                pdf.set_x(10)
                pdf.cell(10, 6, number)
                pdf.multi_cell(0, 6, content)
                pdf.ln(1)

            # ── BULLET POINTS ────────────────────────────────
            elif line.startswith("-"):
                pdf.set_font("Arial", size=11)
                pdf.set_x(15)
                pdf.multi_cell(0, 6, "- " + line[1:].strip())
                pdf.ln(1)

            # ── NORMAL TEXT ──────────────────────────────────
            else:
                pdf.set_font("Arial", size=11)
                pdf.set_x(10)
                pdf.multi_cell(0, 7, line)
                pdf.ln(1)

        # ── Save to file ─────────────────────────────────────
        # Use a unique filename so concurrent requests don't collide
        filename = f"legal_report_{uuid.uuid4().hex[:8]}.pdf"
        file_path = str(OUTPUT_DIR / filename)

        pdf.output(file_path)
        logger.info("📄 PDF report saved: %s", file_path)

        return file_path

    except Exception as exc:
        logger.error("❌ PDF generation failed: %s", exc, exc_info=True)
        raise RuntimeError(f"Failed to generate PDF report: {exc}") from exc

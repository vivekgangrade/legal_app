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
#  CUSTOM THEME
# =====================================================================
def _build_theme() -> gr.themes.Base:
    """Build a premium dark legal theme."""
    return gr.themes.Base(
        primary_hue=gr.themes.Color(
            c50="#eef2ff", c100="#e0e7ff", c200="#c7d2fe",
            c300="#a5b4fc", c400="#818cf8", c500="#6366f1",
            c600="#4f46e5", c700="#4338ca", c800="#3730a3",
            c900="#312e81", c950="#1e1b4b",
        ),
        secondary_hue=gr.themes.Color(
            c50="#f0fdfa", c100="#ccfbf1", c200="#99f6e4",
            c300="#5eead4", c400="#2dd4bf", c500="#14b8a6",
            c600="#0d9488", c700="#0f766e", c800="#115e59",
            c900="#134e4a", c950="#042f2e",
        ),
        neutral_hue=gr.themes.Color(
            c50="#f8fafc", c100="#f1f5f9", c200="#e2e8f0",
            c300="#cbd5e1", c400="#94a3b8", c500="#64748b",
            c600="#475569", c700="#334155", c800="#1e293b",
            c900="#0f172a", c950="#020617",
        ),
        font=gr.themes.GoogleFont("Inter"),
        font_mono=gr.themes.GoogleFont("JetBrains Mono"),
    ).set(
        body_background_fill="#0a0e1a",
        body_background_fill_dark="#0a0e1a",
        body_text_color="#e2e8f0",
        body_text_color_dark="#e2e8f0",
        block_background_fill="#111827",
        block_background_fill_dark="#111827",
        block_border_color="#1e293b",
        block_border_color_dark="#1e293b",
        block_border_width="1px",
        block_label_text_color="#94a3b8",
        block_label_text_color_dark="#94a3b8",
        block_shadow="0 4px 24px rgba(0,0,0,0.3)",
        block_shadow_dark="0 4px 24px rgba(0,0,0,0.3)",
        block_title_text_color="#f1f5f9",
        block_title_text_color_dark="#f1f5f9",
        border_color_primary="#1e293b",
        border_color_primary_dark="#1e293b",
        button_primary_background_fill="linear-gradient(135deg, #6366f1, #8b5cf6)",
        button_primary_background_fill_dark="linear-gradient(135deg, #6366f1, #8b5cf6)",
        button_primary_background_fill_hover="linear-gradient(135deg, #4f46e5, #7c3aed)",
        button_primary_background_fill_hover_dark="linear-gradient(135deg, #4f46e5, #7c3aed)",
        button_primary_text_color="#ffffff",
        button_primary_text_color_dark="#ffffff",
        button_secondary_background_fill="#1e293b",
        button_secondary_background_fill_dark="#1e293b",
        button_secondary_background_fill_hover="#334155",
        button_secondary_background_fill_hover_dark="#334155",
        button_secondary_text_color="#e2e8f0",
        button_secondary_text_color_dark="#e2e8f0",
        input_background_fill="#0f172a",
        input_background_fill_dark="#0f172a",
        input_border_color="#1e293b",
        input_border_color_dark="#1e293b",
        input_border_color_focus="#6366f1",
        input_border_color_focus_dark="#6366f1",
        input_placeholder_color="#475569",
        input_placeholder_color_dark="#475569",
        shadow_spread="8px",
        checkbox_background_color="#1e293b",
        checkbox_background_color_dark="#1e293b",
    )


# =====================================================================
#  CUSTOM CSS
# =====================================================================
CUSTOM_CSS = """
/* ── Google Font Import ───────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Root Variables ───────────────────────────────── */
:root {
    --accent-gradient: linear-gradient(135deg, #6366f1, #8b5cf6, #a78bfa);
    --teal-gradient: linear-gradient(135deg, #14b8a6, #2dd4bf);
    --glass-bg: rgba(17, 24, 39, 0.7);
    --glass-border: rgba(99, 102, 241, 0.15);
    --glow-indigo: 0 0 30px rgba(99, 102, 241, 0.15);
    --glow-teal: 0 0 30px rgba(20, 184, 166, 0.12);
}

/* ── Animated Background ──────────────────────────── */
.gradio-container {
    background: #0a0e1a !important;
    background-image:
        radial-gradient(ellipse at 20% 0%, rgba(99, 102, 241, 0.08) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 100%, rgba(20, 184, 166, 0.06) 0%, transparent 50%) !important;
    min-height: 100vh;
}

/* ── Fade-in Animation ────────────────────────────── */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes shimmer {
    0% { background-position: -200% center; }
    100% { background-position: 200% center; }
}
@keyframes pulse-glow {
    0%, 100% { box-shadow: 0 0 20px rgba(99,102,241,0.1); }
    50% { box-shadow: 0 0 40px rgba(99,102,241,0.2); }
}

/* ── Hero Header ──────────────────────────────────── */
#hero-header {
    text-align: center;
    padding: 2.5rem 1rem 1.5rem;
    animation: fadeInUp 0.8s ease-out;
}
#hero-header h1 {
    font-size: 2.8rem !important;
    font-weight: 800 !important;
    background: linear-gradient(135deg, #c7d2fe, #e0e7ff, #a78bfa) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    letter-spacing: -0.02em;
    margin-bottom: 0.3rem !important;
    line-height: 1.2 !important;
}
#hero-header p {
    color: #94a3b8 !important;
    font-size: 1.05rem !important;
    font-weight: 400;
    margin: 0.3rem 0 !important;
}
#hero-header p:last-child {
    font-size: 0.85rem !important;
    color: #64748b !important;
}

/* ── Stat Cards Row ───────────────────────────────── */
#stat-cards {
    animation: fadeInUp 1s ease-out 0.2s both;
}
#stat-cards .prose {
    display: flex;
    justify-content: center;
    gap: 1rem;
    flex-wrap: wrap;
}

/* ── Tabs ─────────────────────────────────────────── */
.tabs {
    animation: fadeInUp 1s ease-out 0.3s both;
}
button.tab-nav {
    font-weight: 600 !important;
    font-size: 1rem !important;
    padding: 0.85rem 1.8rem !important;
    border-radius: 12px 12px 0 0 !important;
    transition: all 0.3s ease !important;
    border: 1px solid transparent !important;
    border-bottom: none !important;
    color: #94a3b8 !important;
    background: transparent !important;
}
button.tab-nav.selected {
    background: linear-gradient(135deg, rgba(99,102,241,0.15), rgba(139,92,246,0.1)) !important;
    color: #e0e7ff !important;
    border-color: rgba(99,102,241,0.3) !important;
}
button.tab-nav:hover:not(.selected) {
    background: rgba(99,102,241,0.08) !important;
    color: #c7d2fe !important;
}

/* ── Tab Content Panels ───────────────────────────── */
.tabitem {
    background: rgba(17, 24, 39, 0.5) !important;
    border: 1px solid rgba(99, 102, 241, 0.1) !important;
    border-radius: 0 16px 16px 16px !important;
    padding: 1.5rem !important;
    backdrop-filter: blur(20px);
}

/* ── Info Cards (inside tabs) ─────────────────────── */
.info-card {
    background: linear-gradient(135deg, rgba(99,102,241,0.08), rgba(20,184,166,0.05)) !important;
    border: 1px solid rgba(99,102,241,0.15) !important;
    border-radius: 12px !important;
    padding: 1rem 1.2rem !important;
}
.info-card p {
    color: #cbd5e1 !important;
    font-size: 0.95rem !important;
    margin: 0 !important;
}

/* ── File Upload ──────────────────────────────────── */
.upload-area, div[data-testid="file"] {
    border: 2px dashed rgba(99,102,241,0.3) !important;
    border-radius: 16px !important;
    background: rgba(15,23,42,0.6) !important;
    transition: all 0.3s ease !important;
    min-height: 140px !important;
}
.upload-area:hover, div[data-testid="file"]:hover {
    border-color: rgba(99,102,241,0.5) !important;
    background: rgba(99,102,241,0.05) !important;
    box-shadow: var(--glow-indigo) !important;
}

/* ── Textbox Inputs ───────────────────────────────── */
textarea, input[type="text"] {
    background: #0f172a !important;
    border: 1px solid #1e293b !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
    font-size: 0.95rem !important;
    transition: all 0.3s ease !important;
    padding: 0.8rem 1rem !important;
}
textarea:focus, input[type="text"]:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
    outline: none !important;
}

/* ── Buttons ──────────────────────────────────────── */
button.primary {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 0.7rem 1.5rem !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(99,102,241,0.25) !important;
    text-transform: none !important;
}
button.primary:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(99,102,241,0.35) !important;
}
button.primary:active {
    transform: translateY(0) !important;
}
button.secondary {
    background: #1e293b !important;
    border: 1px solid #334155 !important;
    border-radius: 12px !important;
    color: #cbd5e1 !important;
    font-weight: 500 !important;
    transition: all 0.3s ease !important;
}
button.secondary:hover {
    background: #334155 !important;
    border-color: #475569 !important;
}

/* ── Chat Bubbles ─────────────────────────────────── */
.message {
    border-radius: 16px !important;
    padding: 1rem 1.2rem !important;
    line-height: 1.6 !important;
    animation: fadeInUp 0.3s ease-out !important;
}
.message.bot {
    background: linear-gradient(135deg, rgba(99,102,241,0.1), rgba(139,92,246,0.05)) !important;
    border: 1px solid rgba(99,102,241,0.15) !important;
}
.message.user {
    background: rgba(20,184,166,0.1) !important;
    border: 1px solid rgba(20,184,166,0.15) !important;
}

/* ── Markdown Output ──────────────────────────────── */
.prose {
    color: #cbd5e1 !important;
    line-height: 1.7 !important;
}
.prose h1, .prose h2, .prose h3 {
    color: #e0e7ff !important;
    font-weight: 700 !important;
}
.prose strong {
    color: #a5b4fc !important;
}
.prose a {
    color: #818cf8 !important;
    text-decoration: underline !important;
    text-decoration-color: rgba(129,140,248,0.3) !important;
}
.prose code {
    background: #1e293b !important;
    color: #a78bfa !important;
    border-radius: 6px !important;
    padding: 0.15rem 0.4rem !important;
    font-family: 'JetBrains Mono', monospace !important;
}

/* ── Examples ─────────────────────────────────────── */
.examples-row button, table.examples button {
    background: #1e293b !important;
    border: 1px solid #334155 !important;
    border-radius: 10px !important;
    color: #94a3b8 !important;
    font-size: 0.85rem !important;
    padding: 0.5rem 1rem !important;
    transition: all 0.25s ease !important;
}
.examples-row button:hover, table.examples button:hover {
    background: rgba(99,102,241,0.1) !important;
    border-color: rgba(99,102,241,0.3) !important;
    color: #c7d2fe !important;
    transform: translateY(-1px) !important;
}

/* ── Scrollbar ────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0f172a; }
::-webkit-scrollbar-thumb { background: #334155; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #475569; }

/* ── Footer ───────────────────────────────────────── */
#app-footer {
    text-align: center;
    padding: 1.5rem;
    animation: fadeInUp 1.2s ease-out 0.5s both;
}
#app-footer p {
    color: #475569 !important;
    font-size: 0.8rem !important;
}
#app-footer a {
    color: #6366f1 !important;
}

/* ── Responsive ───────────────────────────────────── */
@media (max-width: 768px) {
    #hero-header h1 { font-size: 2rem !important; }
    button.tab-nav { padding: 0.6rem 1rem !important; font-size: 0.9rem !important; }
}

/* ── Labels ───────────────────────────────────────── */
label span {
    color: #94a3b8 !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
}

/* ── Progress Bar ─────────────────────────────────── */
.progress-bar {
    background: var(--accent-gradient) !important;
    border-radius: 999px !important;
}

/* ── Block containers ─────────────────────────────── */
.block {
    border-radius: 16px !important;
    border-color: #1e293b !important;
}
"""


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

        # ── Hero Header ──────────────────────────────────────
        gr.Markdown(
            """
            # ⚖️ Legal AI Platform

            Your intelligent legal assistant powered by cutting-edge AI

            Groq LLaMA 3.1 · FAISS Vector Search · Tavily Web Research
            """,
            elem_id="hero-header",
        )

        # ── Feature Stats ────────────────────────────────────
        with gr.Row(equal_height=True, elem_id="stat-cards"):
            with gr.Column(scale=1, min_width=160):
                gr.Markdown(
                    """<div style="text-align:center;padding:1rem;background:linear-gradient(135deg,rgba(99,102,241,0.12),rgba(139,92,246,0.08));border:1px solid rgba(99,102,241,0.2);border-radius:14px;">
                    <div style="font-size:1.8rem;">📄</div>
                    <div style="color:#e0e7ff;font-weight:700;font-size:1rem;">Document Q&A</div>
                    <div style="color:#64748b;font-size:0.8rem;">RAG-powered answers</div>
                    </div>"""
                )
            with gr.Column(scale=1, min_width=160):
                gr.Markdown(
                    """<div style="text-align:center;padding:1rem;background:linear-gradient(135deg,rgba(20,184,166,0.12),rgba(45,212,191,0.08));border:1px solid rgba(20,184,166,0.2);border-radius:14px;">
                    <div style="font-size:1.8rem;">🔍</div>
                    <div style="color:#ccfbf1;font-weight:700;font-size:1rem;">Legal Research</div>
                    <div style="color:#64748b;font-size:0.8rem;">AI-powered reports</div>
                    </div>"""
                )
            with gr.Column(scale=1, min_width=160):
                gr.Markdown(
                    """<div style="text-align:center;padding:1rem;background:linear-gradient(135deg,rgba(244,114,182,0.12),rgba(251,146,60,0.08));border:1px solid rgba(244,114,182,0.2);border-radius:14px;">
                    <div style="font-size:1.8rem;">📥</div>
                    <div style="color:#fce7f3;font-weight:700;font-size:1rem;">PDF Export</div>
                    <div style="color:#64748b;font-size:0.8rem;">Download reports</div>
                    </div>"""
                )

        gr.HTML("<div style='height:0.5rem'></div>")

        with gr.Tabs():

            # ── TAB 1: Document Q&A (from GenAI) ────────────
            with gr.TabItem("📄 Document Q&A"):
                gr.Markdown(
                    """**Upload legal PDFs** and ask questions about their content.
                    The AI uses Retrieval-Augmented Generation (RAG) to answer from your documents only.""",
                    elem_classes="info-card",
                )

                doc_chat = gr.ChatInterface(
                    fn=document_qa,
                    additional_inputs=[
                        gr.File(
                            label="📁 Upload Legal PDFs",
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
                    """**Enter a legal topic** to generate a professionally researched report
                    using real-time web sources. Download as PDF when ready.""",
                    elem_classes="info-card",
                )

                gr.HTML("<div style='height:0.8rem'></div>")

                query_input = gr.Textbox(
                    label="🔎 Enter Legal Query",
                    placeholder="e.g. What are cybercrime laws in India under IT Act 2000?",
                    lines=2,
                )

                with gr.Row():
                    research_btn = gr.Button(
                        "🔍 Generate Research Report",
                        variant="primary",
                        scale=3,
                    )
                    clear_btn = gr.Button("🗑️ Clear", variant="secondary", scale=1)

                gr.HTML("<div style='height:0.5rem'></div>")

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

                gr.HTML("<div style='height:0.5rem'></div>")

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
            """---
            Built with ❤️ — Merging GenAI (RAG) + Agentic AI (Web Research) into one unified platform.
            """,
            elem_id="app-footer",
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
        "theme": _build_theme(),
        "css": CUSTOM_CSS,
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

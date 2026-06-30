from __future__ import annotations

from html import escape
from pathlib import Path

import streamlit as st

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

from bilingual_productivity_llm.common.schemas import GenerationRequest, NoteToStructureExample
from bilingual_productivity_llm.common.tasks import TASK_SCHEMAS
from bilingual_productivity_llm.eval.validators import validate_example
from bilingual_productivity_llm.inference.backend import generate_structured_output


TASK_OPTIONS = [
    "meeting_minutes",
    "project_report",
    "study_notes",
    "professional_summary",
]

LANGUAGE_OPTIONS = ["de", "en", "mixed"]


def _inject_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background:
                linear-gradient(180deg, #f8f4ed 0%, #f4ede4 50%, #efe6da 100%);
            color: #1b2430;
        }
        .block-container {
            max-width: none;
            padding-top: 1.5rem;
            padding-bottom: 2rem;
            padding-left: 2rem;
            padding-right: 2rem;
        }
        h1, h2, h3, h4, h5, h6, p, li, label, span, div {
            color: inherit;
        }
        .hero-simple {
            background: rgba(255, 251, 245, 0.92);
            border: 1px solid rgba(16, 37, 66, 0.10);
            border-radius: 20px;
            padding: 1.1rem 1.2rem;
            margin-bottom: 1rem;
            box-shadow: 0 12px 28px rgba(16, 37, 66, 0.08);
        }
        .hero-simple h1 {
            margin: 0 0 0.35rem 0;
            color: #162334 !important;
            font-size: 2.1rem;
            line-height: 1.08;
        }
        .hero-simple p {
            margin: 0;
            color: #334155 !important;
            font-size: 1rem;
            max-width: 880px;
        }
        .mini-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.8rem;
            margin: 1rem 0 1.4rem 0;
        }
        .mini-card {
            background: rgba(255, 250, 244, 0.96);
            border: 1px solid rgba(16, 37, 66, 0.09);
            border-radius: 18px;
            padding: 0.9rem 1rem;
            box-shadow: 0 14px 32px rgba(16, 37, 66, 0.08);
        }
        .mini-card strong {
            display: block;
            color: #173f6d;
            font-size: 0.86rem;
            letter-spacing: 0.02em;
        }
        .mini-card span {
            color: #473729;
            font-size: 0.95rem;
        }
        .section-label {
            font-size: 0.88rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #6e5842;
            margin-bottom: 0.5rem;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #f7efe1 0%, #efe3d0 100%);
            border-right: 1px solid rgba(16, 37, 66, 0.08);
        }
        [data-testid="stSidebar"] > div:first-child {
            background: transparent;
        }
        [data-testid="stTextArea"] textarea {
            background: rgba(255, 252, 247, 0.98) !important;
            color: #1a2330 !important;
            border-radius: 18px !important;
            border: 1px solid rgba(16, 37, 66, 0.14) !important;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.7);
        }
        [data-testid="stFileUploader"] section,
        [data-testid="stMetric"],
        div[data-testid="stAlertContainer"] > div {
            background: rgba(255, 251, 245, 0.96) !important;
            border: 1px solid rgba(16, 37, 66, 0.10) !important;
            border-radius: 20px !important;
            box-shadow: 0 16px 36px rgba(16, 37, 66, 0.08) !important;
        }
        [data-testid="stVerticalBlockBorderWrapper"] {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }
        [data-testid="stTabs"] {
            background: transparent !important;
        }
        [data-testid="stMetricValue"] {
            color: #18324d !important;
        }
        [data-testid="stMetricLabel"] p,
        [data-testid="stMarkdownContainer"] p,
        [data-testid="stMarkdownContainer"] li,
        [data-testid="stMarkdownContainer"] strong,
        [data-testid="stMarkdownContainer"] h1,
        [data-testid="stMarkdownContainer"] h2,
        [data-testid="stMarkdownContainer"] h3,
        [data-testid="stMarkdownContainer"] h4 {
            color: #1b2430 !important;
        }
        [data-testid="stSelectbox"] > div,
        [data-testid="stFileUploader"] label,
        [data-testid="stTextArea"] label,
        [data-testid="stToggle"] label {
            color: #1b2430 !important;
        }
        .preview-panel {
            background: rgba(255, 251, 245, 0.98);
            border: 1px solid rgba(16, 37, 66, 0.10);
            border-radius: 22px;
            padding: 1rem 1.1rem;
            box-shadow: 0 16px 36px rgba(16, 37, 66, 0.08);
            color: #1b2430;
            min-height: 260px;
            max-height: 420px;
            overflow: auto;
            white-space: pre-wrap;
            line-height: 1.55;
            font-size: 0.98rem;
        }
        .download-row {
            margin-top: 0.9rem;
        }
        .result-panel {
            background: rgba(255, 251, 245, 0.95);
            border: 1px solid rgba(16, 37, 66, 0.10);
            border-radius: 22px;
            padding: 1rem 1.1rem;
            box-shadow: 0 16px 36px rgba(16, 37, 66, 0.08);
        }
        [data-testid="stButton"] button,
        [data-testid="stDownloadButton"] button {
            border-radius: 14px !important;
            border: 0 !important;
            background: linear-gradient(135deg, #173f6d 0%, #275f9b 100%) !important;
            color: #fffdf8 !important;
            font-weight: 600 !important;
            box-shadow: 0 14px 28px rgba(23, 63, 109, 0.20) !important;
        }
        [data-testid="stButton"] button:hover,
        [data-testid="stDownloadButton"] button:hover {
            background: linear-gradient(135deg, #102d4e 0%, #1d4f85 100%) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_hero() -> None:
    st.markdown(
        """
        <div class="hero-simple">
            <h1>Bilingual Notes To Structured Writing</h1>
            <p>
                Upload German or English notes, paste text directly, and generate clean meeting minutes,
                study notes, reports, or professional summaries with structure and validation feedback.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="mini-grid">
            <div class="mini-card"><strong>Inputs</strong><span>PDF, text, markdown, and other file uploads plus manual note entry</span></div>
            <div class="mini-card"><strong>Outputs</strong><span>Structured markdown aligned to fixed schemas</span></div>
            <div class="mini-card"><strong>Checks</strong><span>Schema, citation, section-order, and warning signals</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def _extract_text_from_upload(uploaded: st.runtime.uploaded_file_manager.UploadedFile) -> str:
    suffix = Path(uploaded.name).suffix.lower()

    if suffix == ".pdf":
        if PdfReader is None:
            return ""
        try:
            reader = PdfReader(uploaded)
            text = "\n".join((page.extract_text() or "").strip() for page in reader.pages)
            uploaded.seek(0)
            return text.strip()
        except Exception:
            uploaded.seek(0)
            return ""

    try:
        return uploaded.getvalue().decode("utf-8").strip()
    except UnicodeDecodeError:
        try:
            return uploaded.getvalue().decode("latin-1", errors="ignore").strip()
        except Exception:
            return ""


def _read_uploaded_notes(
    uploaded_files: list[st.runtime.uploaded_file_manager.UploadedFile],
) -> tuple[str, list[str]]:
    chunks: list[str] = []
    unreadable: list[str] = []

    for uploaded in uploaded_files:
        content = _extract_text_from_upload(uploaded)
        if content.strip():
            chunks.append(f"# File: {uploaded.name}\n{content.strip()}")
        else:
            unreadable.append(uploaded.name)

    return "\n\n".join(chunks), unreadable


def _load_sample_notes() -> dict[str, str]:
    sample_dir = Path("data/raw")
    samples: dict[str, str] = {}
    for path in sorted(sample_dir.rglob("*")):
        if path.is_file() and path.suffix.lower() in {".txt", ".md"}:
            samples[str(path.relative_to(sample_dir))] = path.read_text(encoding="utf-8").strip()
    return samples


def _compose_notes(uploaded_text: str, manual_text: str) -> str:
    parts = [part.strip() for part in [uploaded_text, manual_text] if part.strip()]
    return "\n\n".join(parts)


def _render_preview(text: str) -> None:
    display = escape(text[:12000]) if text.strip() else "No input notes yet."
    st.markdown(
        f'<div class="preview-panel">{display}</div>',
        unsafe_allow_html=True,
    )


def _metric_card(label: str, value: str) -> None:
    st.markdown(
        f"""
        <div class="mini-card">
            <strong>{label}</strong>
            <span>{value}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(
        page_title="Bilingual Productivity LLM",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    _inject_styles()
    _render_hero()

    samples = _load_sample_notes()

    with st.sidebar:
        st.markdown("### Generation Setup")
        task = st.selectbox("Task type", TASK_OPTIONS, index=0)
        language = st.selectbox("Output language", LANGUAGE_OPTIONS, index=0)
        citation_style = st.selectbox("Citation style", ["apa-like"], index=0)
        strict_structure = st.toggle("Strict structure mode", value=True)
        st.markdown("### Input Options")
        sample_choice = st.selectbox(
            "Load a sample note file",
            ["None"] + list(samples.keys()),
            index=0,
        )

    default_text = samples.get(sample_choice, "") if sample_choice != "None" else ""

    left, right = st.columns([1.3, 1], gap="large")
    with left:
        st.markdown('<div class="section-label">Input Workspace</div>', unsafe_allow_html=True)
        uploaded_files = st.file_uploader(
            "Upload note files",
            accept_multiple_files=True,
            help="Upload notes in common formats such as TXT, MD, or PDF. Extracted content is combined with the text area below.",
        )
        manual_notes = st.text_area(
            "Paste or edit notes",
            value=default_text,
            height=320,
            placeholder="Paste meeting notes, class notes, project bullets, or a bilingual note dump here...",
        )
        uploaded_notes, unreadable_files = _read_uploaded_notes(uploaded_files or [])
        combined_notes = _compose_notes(uploaded_notes, manual_notes)

        preview_tab, upload_tab = st.tabs(["Combined Notes", "Uploaded Files"])
        with preview_tab:
            _render_preview(combined_notes)
        with upload_tab:
            if uploaded_files:
                for item in uploaded_files:
                    st.write(f"- {item.name}")
                if unreadable_files:
                    st.warning(
                        "Could not extract preview text from: " + ", ".join(unreadable_files)
                    )
            else:
                st.caption("No files uploaded yet.")

        generate = st.button("Generate Structured Output", type="primary", use_container_width=True)

    with right:
        st.markdown('<div class="section-label">Current Settings</div>', unsafe_allow_html=True)
        st.markdown('<div class="mini-grid">', unsafe_allow_html=True)
        _metric_card("Task", task.replace("_", " ").title())
        _metric_card("Language", language.upper())
        _metric_card("Citation Style", citation_style)
        st.markdown("</div>", unsafe_allow_html=True)
        st.info(
            "The current backend is a validated heuristic demo layer. Replace it with a trained checkpoint later without changing the UI flow."
        )

    if generate:
        generation = generate_structured_output(
            GenerationRequest(
                task=task,
                language=language,
                citation_style=citation_style,
                notes=combined_notes,
                strict_structure=strict_structure,
            )
        )
        example = NoteToStructureExample(
            example_id="demo",
            task=task,
            language=language,
            citation_style=citation_style,
            notes=combined_notes,
            target=generation.output_text,
            key_facts=generation.extracted_key_facts,
            required_sections=TASK_SCHEMAS[task],
        )
        validation = validate_example(example)

        st.markdown("---")
        result_left, result_middle, result_right = st.columns([1.6, 1, 1], gap="large")

        with result_left:
            st.markdown('<div class="section-label">Generated Output</div>', unsafe_allow_html=True)
            st.markdown('<div class="result-panel">', unsafe_allow_html=True)
            st.markdown(generation.output_text)
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown('<div class="download-row">', unsafe_allow_html=True)
            st.download_button(
                "Download Markdown",
                generation.output_text,
                file_name=f"{task}.md",
                mime="text/markdown",
                use_container_width=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)

        with result_middle:
            st.markdown('<div class="section-label">Extracted Facts</div>', unsafe_allow_html=True)
            st.markdown('<div class="result-panel">', unsafe_allow_html=True)
            if generation.extracted_key_facts:
                for fact in generation.extracted_key_facts:
                    st.write(f"- {fact}")
            else:
                st.caption("No key facts extracted.")
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown('<div class="section-label">Generation Warnings</div>', unsafe_allow_html=True)
            st.markdown('<div class="result-panel">', unsafe_allow_html=True)
            if generation.warnings:
                for warning in generation.warnings:
                    st.warning(warning)
            else:
                st.success("No generation warnings.")
            st.markdown("</div>", unsafe_allow_html=True)

        with result_right:
            st.markdown('<div class="section-label">Validation</div>', unsafe_allow_html=True)
            st.markdown('<div class="result-panel">', unsafe_allow_html=True)
            st.metric("Schema OK", "Yes" if validation.schema_ok else "No")
            st.metric("Section Order OK", "Yes" if validation.section_order_ok else "No")
            st.metric("Citation Present", "Yes" if validation.citation_present else "No")
            st.metric("Key Fact Coverage", f"{validation.key_fact_coverage:.2f}")
            if validation.missing_sections:
                st.error(f"Missing: {', '.join(validation.missing_sections)}")
            if validation.unsupported_output_facts:
                st.warning("Potential unsupported items:")
                for item in validation.unsupported_output_facts:
                    st.write(f"- {item}")
            if validation.warnings:
                st.info("Validator notes:")
                for warning in validation.warnings:
                    st.write(f"- {warning}")
            st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()

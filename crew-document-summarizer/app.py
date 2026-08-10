"""
app.py
------
The Streamlit web interface for the AI Document Summarizer.

Flow:
    1. User uploads a PDF.
    2. We extract its text (document_processor.py).
    3. We send the text through the CrewAI workflow (crew.py).
    4. We display the final summary and key points.
"""

import logging
import os
import re

import streamlit as st
from dotenv import load_dotenv

from document_processor import extract_text_from_pdf, DocumentProcessingError
from agents import MissingApiKeyError
from crew import run_summarization, SummarizationError

# Load variables from the .env file (e.g. GEMINI_API_KEY) into the environment.
load_dotenv()

# Print full tracebacks to the terminal running `streamlit run app.py` so
# the real backend error is visible during development, instead of only
# the friendly message shown in the browser UI.
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


def parse_summary_output(raw_text):
    """
    Split the agent's raw output into a summary and a list of key points,
    based on the "SUMMARY:" / "KEY POINTS:" markers we asked the agent to use.

    Falls back gracefully if the agent didn't follow the format exactly.

    Returns:
        tuple: (summary_text: str, key_points: list[str])
    """
    match = re.search(
        r"SUMMARY:\s*(.*?)\s*KEY POINTS:\s*(.*)",
        raw_text,
        re.IGNORECASE | re.DOTALL,
    )

    if not match:
        # Agent didn't use the expected format - just show everything as the summary.
        return raw_text.strip(), []

    summary_text = match.group(1).strip()
    points_block = match.group(2).strip()

    key_points = [
        line.lstrip("-*• ").strip()
        for line in points_block.splitlines()
        if line.strip()
    ]

    return summary_text, key_points


def main():
    st.set_page_config(
        page_title="AI Document Summarizer",
        page_icon="📄",
        layout="centered",
    )

    st.title("📄 AI Document Summarizer")
    st.caption("Built with CrewAI — an internship project demonstrating AI agents & tasks")

    st.write(
        "Upload a PDF document and let an AI agent read it for you. "
        "The app will extract the text and generate a concise summary "
        "along with the key points."
    )

    st.divider()

    uploaded_file = st.file_uploader("Upload a PDF document", type=["pdf"])

    if uploaded_file is not None:
        st.success(f"📎 Uploaded file: **{uploaded_file.name}**")

    summarize_clicked = st.button(
        "✨ Summarize Document",
        type="primary",
        disabled=uploaded_file is None,
    )

    if not summarize_clicked:
        return

    if uploaded_file is None:
        st.warning("Please upload a PDF file first.")
        return

    # --- Step 1: Extract text from the PDF ---
    with st.spinner("Reading and extracting text from your PDF..."):
        try:
            document_text, num_pages = extract_text_from_pdf(uploaded_file)
        except DocumentProcessingError as exc:
            st.error(f"⚠️ {exc}")
            return

    st.subheader("📋 Document Information")
    col1, col2 = st.columns(2)
    col1.metric("Pages", num_pages)
    col2.metric("Characters Extracted", f"{len(document_text):,}")

    # --- Step 2: Run the CrewAI summarization workflow ---
    with st.spinner("The AI agent is analyzing and summarizing your document... This may take a moment."):
        try:
            raw_result = run_summarization(document_text)
        except MissingApiKeyError as exc:
            st.error(f"🔑 {exc}")
            return
        except SummarizationError as exc:
            st.error("😕 We couldn't generate a summary for this document.")
            with st.expander("Technical details"):
                st.code(str(exc))
            return
        except Exception as exc:  # final safety net - never show a raw traceback
            logger.exception("Unexpected error during summarization")
            st.error("😕 Something unexpected went wrong while summarizing the document.")
            with st.expander("Technical details"):
                st.code(f"[{type(exc).__name__}] {exc}")
            return

    # --- Step 3: Display the results ---
    summary_text, key_points = parse_summary_output(raw_result)

    st.divider()
    st.subheader("🧠 Summary")
    st.write(summary_text)

    if key_points:
        st.subheader("🔑 Key Points")
        for point in key_points:
            st.markdown(f"- {point}")

    st.success("Done! You can upload another document to try again.")


if __name__ == "__main__":
    main()

"""
document_processor.py
----------------------
Handles everything related to reading an uploaded PDF file and turning it
into plain text that can be sent to the CrewAI agent.

This module has NO CrewAI code in it on purpose - it only knows about PDFs
and text. This keeps the project modular and easy to understand.
"""

from pypdf import PdfReader
from pypdf.errors import PdfReadError


# If the extracted text is longer than this, we split it into chunks
# before summarizing so we don't send too much text to the LLM at once.
# Gemini Flash has a much larger context window than the GPT-4o-mini this
# threshold was originally tuned for, so it's set high here - chunking still
# kicks in for genuinely large documents, but normal-sized PDFs no longer
# get split into many small pieces that each need a separate free-tier
# Gemini call (which was tripping Gemini's per-minute rate limit).
MAX_CHARS_BEFORE_CHUNKING = 100000

# Size of each chunk (in characters) when the document is large.
CHUNK_SIZE = 60000


class DocumentProcessingError(Exception):
    """Raised when a PDF cannot be read or contains no usable text."""
    pass


def extract_text_from_pdf(uploaded_file):
    """
    Extract text from a Streamlit-uploaded PDF file.

    Args:
        uploaded_file: A file-like object from st.file_uploader().

    Returns:
        tuple: (full_text: str, num_pages: int)

    Raises:
        DocumentProcessingError: If the file is not a valid PDF,
            is empty, or has no extractable text.
    """
    try:
        reader = PdfReader(uploaded_file)
    except PdfReadError:
        raise DocumentProcessingError(
            "This file could not be read as a PDF. Please upload a valid PDF document."
        )
    except Exception:
        raise DocumentProcessingError(
            "The uploaded file is invalid or corrupted. Please try a different file."
        )

    num_pages = len(reader.pages)

    if num_pages == 0:
        raise DocumentProcessingError("The uploaded PDF has no pages.")

    extracted_pages = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        extracted_pages.append(page_text)

    full_text = "\n".join(extracted_pages).strip()

    if not full_text:
        raise DocumentProcessingError(
            "No readable text was found in this PDF. It may be a scanned "
            "image or a document without a text layer, which this app "
            "cannot process yet."
        )

    return full_text, num_pages


def split_text_into_chunks(text, chunk_size=CHUNK_SIZE):
    """
    Split a long piece of text into smaller chunks so it fits comfortably
    inside the LLM's context window.

    This is a simple character-based split (not sentence-aware) which is
    good enough for a beginner-friendly project.

    Args:
        text: The full document text.
        chunk_size: Maximum number of characters per chunk.

    Returns:
        list[str]: A list of text chunks.
    """
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]


def needs_chunking(text):
    """Return True if the document is long enough to require chunking."""
    return len(text) > MAX_CHARS_BEFORE_CHUNKING

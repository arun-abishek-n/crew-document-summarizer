"""
crew.py
-------
Builds and runs the CrewAI Crew for this project.

WORKFLOW
--------
    document text
        -> (if large) split into chunks
        -> Agent + Task(s)
        -> Crew.kickoff()
        -> final summary text

For a normal-sized document we use the simplest possible setup:
    1 Agent + 1 Task + 1 Crew

For a very large document, we still use the SAME single agent, but give
it several small "chunk summary" tasks followed by one "combine" task,
so the whole thing still runs as a single Crew with one sequential
process. This avoids exceeding the LLM's context window while staying
simple to follow.
"""

import logging

from crewai import Crew, Process

from agents import get_llm, create_summarizer_agent
from tasks import (
    create_summarization_task,
    create_chunk_summary_task,
    create_final_combination_task,
)
from document_processor import split_text_into_chunks, needs_chunking

logger = logging.getLogger(__name__)


class SummarizationError(Exception):
    """Raised when the Crew fails to produce a summary."""
    pass


def run_summarization(document_text):
    """
    Run the full CrewAI workflow on the given document text and return
    the final summary as a string.

    Args:
        document_text: The extracted text of the uploaded PDF.

    Returns:
        str: The final summary (including SUMMARY and KEY POINTS sections).

    Raises:
        MissingApiKeyError: If no Gemini API key is configured.
        SummarizationError: If the LLM/Crew call fails for any other reason.
    """
    llm = get_llm()  # may raise MissingApiKeyError - let it propagate
    agent = create_summarizer_agent(llm)

    try:
        if needs_chunking(document_text):
            result = _run_chunked_crew(agent, document_text)
        else:
            result = _run_simple_crew(agent, document_text)
    except Exception as exc:
        # Log the full traceback to the console/terminal so the real cause
        # (e.g. a Gemini rate limit, auth error, or timeout) is visible to
        # the developer, even though the Streamlit UI only shows a friendly
        # message plus a short "Technical details" summary.
        logger.exception("CrewAI summarization failed")

        # Wrap any LLM/network/CrewAI error into a friendly, catch-all error
        # so the Streamlit UI can display a clean message instead of a
        # raw stack trace. The exception type is included so the short
        # message shown in the UI still points at the real cause.
        raise SummarizationError(
            f"[{type(exc).__name__}] {exc}"
        ) from exc

    return str(result).strip()


def _run_simple_crew(agent, document_text):
    """The simple, one-agent-one-task path used for normal-sized documents."""
    task = create_summarization_task(agent, document_text)

    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True,
    )

    return crew.kickoff()


def _run_chunked_crew(agent, document_text):
    """The chunk-then-combine path used for very large documents."""
    chunks = split_text_into_chunks(document_text)
    total_chunks = len(chunks)

    chunk_tasks = [
        create_chunk_summary_task(agent, chunk, i + 1, total_chunks)
        for i, chunk in enumerate(chunks)
    ]
    final_task = create_final_combination_task(agent, context_tasks=chunk_tasks)

    crew = Crew(
        agents=[agent],
        tasks=chunk_tasks + [final_task],
        process=Process.sequential,
        verbose=True,
    )

    return crew.kickoff()

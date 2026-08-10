"""
tasks.py
--------
Defines the CrewAI Task(s) for the document summarization workflow.

Two kinds of tasks are provided:

1. create_summarization_task()
   Used for normal-sized documents. A single task reads the whole
   document and produces the final summary + key points.

2. create_chunk_summary_task() / create_final_combination_task()
   Used only when the document is very large. Each chunk is summarized
   individually first, then a final task combines those mini-summaries
   into one coherent summary. This keeps the project simple while still
   handling large documents safely (see document_processor.py).
"""

from crewai import Task


OUTPUT_FORMAT_INSTRUCTIONS = (
    "Format your final answer EXACTLY like this:\n\n"
    "SUMMARY:\n"
    "<a clear, concise summary in 2-5 short paragraphs>\n\n"
    "KEY POINTS:\n"
    "- <key point 1>\n"
    "- <key point 2>\n"
    "- <key point 3>\n"
    "(include 5-8 key points total)"
)


def create_summarization_task(agent, document_text):
    """
    Create the main summarization task for a normal-sized document.

    Args:
        agent: The summarizer Agent.
        document_text: The full extracted text of the document.

    Returns:
        crewai.Task
    """
    return Task(
        description=(
            "Read the following document text carefully and summarize it.\n\n"
            "DOCUMENT TEXT:\n"
            "\"\"\"\n"
            f"{document_text}\n"
            "\"\"\"\n\n"
            f"{OUTPUT_FORMAT_INSTRUCTIONS}"
        ),
        expected_output=(
            "A well-formatted response containing a SUMMARY section and a "
            "KEY POINTS section, exactly as instructed."
        ),
        agent=agent,
    )


def create_chunk_summary_task(agent, chunk_text, chunk_number, total_chunks):
    """
    Create a task that summarizes ONE chunk of a large document.

    Args:
        agent: The summarizer Agent.
        chunk_text: The text of this particular chunk.
        chunk_number: 1-based index of this chunk.
        total_chunks: Total number of chunks the document was split into.

    Returns:
        crewai.Task
    """
    return Task(
        description=(
            f"This is part {chunk_number} of {total_chunks} of a larger document. "
            "Read this part and write a short, factual mini-summary (3-5 sentences) "
            "capturing its main ideas. Do not add information that isn't in the text.\n\n"
            "TEXT:\n"
            "\"\"\"\n"
            f"{chunk_text}\n"
            "\"\"\""
        ),
        expected_output="A short 3-5 sentence mini-summary of this part of the document.",
        agent=agent,
    )


def create_final_combination_task(agent, context_tasks):
    """
    Create the final task that merges all chunk mini-summaries into one
    coherent summary. CrewAI automatically passes the outputs of the
    tasks listed in `context_tasks` into this task.

    Args:
        agent: The summarizer Agent.
        context_tasks: List of chunk-summary Tasks whose outputs should
            be combined.

    Returns:
        crewai.Task
    """
    return Task(
        description=(
            "You have been given several mini-summaries, each covering one part "
            "of the same document. Combine them into a single, coherent final "
            "summary of the WHOLE document. Remove repetition and keep it concise.\n\n"
            f"{OUTPUT_FORMAT_INSTRUCTIONS}"
        ),
        expected_output=(
            "A well-formatted response containing a SUMMARY section and a "
            "KEY POINTS section, exactly as instructed."
        ),
        agent=agent,
        context=context_tasks,
    )

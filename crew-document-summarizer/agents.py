"""
agents.py
---------
Defines the CrewAI Agent(s) used in this project and the LLM that powers
them.

For this beginner project we use exactly ONE agent:

    Document Analyst / Summarizer
        - Reads the extracted document text
        - Produces a clear, concise summary with key points

Keeping it to a single agent makes the CrewAI concepts easy to follow.
"""

import os
from crewai import Agent, LLM


class MissingApiKeyError(Exception):
    """Raised when GEMINI_API_KEY is not set in the environment."""
    pass


def get_llm():
    """
    Build the LLM object used by our agent.

    The API key is read ONLY from the environment (via the .env file).
    It is never hardcoded and never shown in the UI.

    Returns:
        crewai.LLM: A configured LLM instance.

    Raises:
        MissingApiKeyError: If GEMINI_API_KEY is not set.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise MissingApiKeyError(
            "GEMINI_API_KEY is missing. Please copy .env.example to .env "
            "and add your Gemini API key (get one for free at "
            "https://aistudio.google.com/apikey) before running this app."
        )

    # CrewAI uses LiteLLM under the hood. The "gemini/" prefix tells LiteLLM
    # to call Google's Gemini API (via GEMINI_API_KEY) instead of OpenAI.
    model_name = os.getenv("GEMINI_MODEL_NAME", "gemini/gemini-flash-latest")

    # num_retries lets LiteLLM automatically retry (with backoff) on
    # transient errors such as Gemini's free-tier rate limiting, which is
    # the most common cause of summarization failures on real documents.
    return LLM(model=model_name, api_key=api_key, temperature=0.3, num_retries=3)


def create_summarizer_agent(llm):
    """
    Create the single agent used in this project: a Document Analyst
    whose job is to read text and produce a summary.

    Args:
        llm: The LLM instance returned by get_llm().

    Returns:
        crewai.Agent
    """
    return Agent(
        role="Document Analyst and Summarizer",
        goal=(
            "Carefully read the provided document text and produce a clear, "
            "accurate, and concise summary along with the most important key points."
        ),
        backstory=(
            "You are an experienced research analyst who specializes in reading "
            "long documents and distilling them into short, easy-to-understand "
            "summaries for busy readers. You always stay faithful to the source "
            "text and never invent information that isn't there."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

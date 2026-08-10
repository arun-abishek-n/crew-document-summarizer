# AI Document Summarizer using CrewAI

An learning project that demonstrates the core concepts of
**CrewAI** (Agents, Tasks, and Crews) by building a small, practical
application: upload a PDF, and get back an AI-generated summary and key
points.

---

## Overview

This project was built while learning CrewAI as part of an internship.
The goal was to watch a CrewAI tutorial and implement one small, real
use case end-to-end — not just a toy script, but a working app with a
UI, error handling, and a clean project structure.

**Use case implemented:** *Summarize Uploaded Documents using CrewAI.*

---

## Problem Statement

Reading long documents (reports, articles, contracts, research papers)
takes time. People often just want the main ideas without reading every
page. Manually summarizing documents is slow and repetitive — a perfect
small task to automate with an AI agent.

---

## Solution

The app lets a user upload a PDF through a simple Streamlit web page.
The text is extracted from the PDF and handed to a CrewAI **Agent**,
which reads it and produces:

- A short, clear **summary**
- A list of **key points**

If the document is very large, it is automatically split into chunks,
summarized in parts, and then combined into one final summary — all
within the same CrewAI Crew.

---

## Features

- 📤 Upload any text-based PDF document
- 📄 Automatic text extraction (with page count shown)
- 🤖 AI summarization powered by a CrewAI Agent + Task + Crew
- 🧩 Safe handling of large documents via simple text chunking
- 🖥️ Clean, beginner-friendly Streamlit interface
- 🔑 API key handled securely via environment variables (never hardcoded)
- ⚠️ User-friendly error messages for invalid files, empty PDFs, and
  missing/incorrect API keys

---

## Technologies Used

| Technology     | Purpose                                   |
|----------------|--------------------------------------------|
| Python         | Core programming language                 |
| CrewAI         | Multi-agent AI orchestration framework     |
| Google Gemini API | The LLM that powers the summarizer agent |
| pypdf          | Extracting text from uploaded PDF files    |
| Streamlit      | Simple web interface                       |
| python-dotenv  | Loading the API key from a `.env` file     |

---

## CrewAI Architecture

### What is CrewAI?

CrewAI is a Python framework for building applications powered by
**multiple AI agents working together**, similar to a team of coworkers
each with their own role. Instead of writing one giant prompt, you
describe *who* does the work (Agents), *what* needs to be done (Tasks),
and CrewAI (the Crew) coordinates everything and runs it through an LLM.

### What is an Agent?

An **Agent** is an AI worker with:
- a **role** (e.g. "Document Analyst")
- a **goal** (what it's trying to achieve)
- a **backstory** (context that shapes how it behaves)
- an **LLM** that actually powers its "thinking"

Think of an Agent as a specialized employee you can assign work to.

### What is a Task?

A **Task** is a specific piece of work given to an Agent. It has:
- a **description** (detailed instructions, often including the input data)
- an **expected_output** (what a good result looks like)
- an **agent** (who is responsible for completing it)

### What is a Crew?

A **Crew** is the manager that brings Agents and Tasks together and
actually runs the workflow. You give it a list of agents, a list of
tasks, and a process (in this project: `sequential`, meaning tasks run
one after another). Calling `crew.kickoff()` executes the whole thing
and returns the final result.

### How are they connected in this project?

```
                 USER
                  |
             Upload PDF
                  |
     Extract text (document_processor.py)
                  |
        ┌─────────────────────┐
        │        CREW         │   <- crew.py
        │  ┌────────────────┐  │
        │  │     AGENT      │  │   <- agents.py
        │  │ Document       │  │      "Document Analyst / Summarizer"
        │  │ Analyst /      │  │
        │  │ Summarizer     │  │
        │  └───────┬────────┘  │
        │          │           │
        │  ┌───────▼────────┐  │
        │  │      TASK      │  │   <- tasks.py
        │  │ Summarize the  │  │      "Summarization Task"
        │  │ document text  │  │
        │  └───────┬────────┘  │
        └──────────┼───────────┘
                    │
             crew.kickoff()
                    │
             Final Summary
                    │
           Displayed in Streamlit
```

For this project specifically:

- **Agent:** *Document Analyst / Summarizer* — reads text and writes summaries.
- **Task:** *Document Summarization Task* — "Analyze the uploaded document
  and generate a concise summary with key points."
- **Crew:** Runs the agent through the task(s) sequentially and returns
  the final result.

For very large documents, the Crew instead runs several small
"summarize this chunk" Tasks (same Agent) followed by one "combine
everything" Task — still one Agent, just a couple of extra Tasks. This
is handled automatically; you don't need to do anything different in
the UI.

---

## Project Structure

```
crew-document-summarizer/
│
├── app.py                  # Streamlit web interface (entry point)
├── crew.py                 # Builds and runs the CrewAI Crew
├── agents.py                # Defines the LLM and the Summarizer Agent
├── tasks.py                 # Defines the summarization Task(s)
├── document_processor.py    # PDF text extraction + chunking logic
├── requirements.txt         # Python dependencies
├── .env.example              # Template for your API key (safe to commit)
├── .gitignore
├── README.md
└── sample/
    └── README.md            # Notes on where to put test PDFs
```

---

## Installation

### Prerequisites

- Python 3.10 – 3.13 installed
- A free Gemini API key ([aistudio.google.com/apikey](https://aistudio.google.com/apikey))

### Step-by-step (Windows)

```bash
# 1. Create a virtual environment
python -m venv venv

# 2. Activate it
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

**What each command does:**
- `python -m venv venv` — creates an isolated Python environment in a
  folder called `venv`, so this project's packages don't clash with
  other projects on your machine.
- `venv\Scripts\activate` — activates that environment (you'll see
  `(venv)` appear in your terminal prompt).
- `pip install -r requirements.txt` — installs CrewAI, Streamlit, pypdf,
  and python-dotenv, exactly as listed in `requirements.txt`.

---

## Environment Setup

1. Copy the example environment file:

   ```bash
   copy .env.example .env
   ```

2. Open `.env` in a text editor and paste in your real Gemini API key:

   ```
   GEMINI_API_KEY=your-real-key-here
   GEMINI_MODEL_NAME=gemini/gemini-flash-latest
   ```

3. Save the file. **Never share or commit this `.env` file** — it's
   already excluded via `.gitignore`.

---

## How to Run

```bash
streamlit run app.py
```

This starts a local web server and automatically opens the app in your
browser (usually at `http://localhost:8501`).

To stop the app, go back to the terminal and press `Ctrl + C`.

---

## How It Works

1. **Upload** — You choose a PDF file in the Streamlit UI.
2. **Extract** — `document_processor.py` uses `pypdf` to read every page
   and combine the text into one string.
3. **Chunk (if needed)** — If the extracted text is very long, it's
   split into smaller pieces so the LLM can process it reliably.
4. **Agent + Task** — `agents.py` creates a "Document Analyst" Agent.
   `tasks.py` creates a Task instructing that agent to read the text and
   produce a `SUMMARY:` section and a `KEY POINTS:` section.
5. **Crew** — `crew.py` puts the Agent and Task(s) into a `Crew` and
   calls `crew.kickoff()`, which sends everything to the LLM (Google
   Gemini) and returns the result.
6. **Display** — `app.py` parses the result and shows the summary and
   key points nicely in the browser.

---

## Example Usage

1. Run `streamlit run app.py`.
2. Click **"Upload a PDF document"** and select a report or article.
3. Click **"✨ Summarize Document"**.
4. Wait a few seconds while the spinner shows "The AI agent is analyzing...".
5. View the **Summary** and **Key Points** sections that appear below.

---

## Expected Output

For a normal PDF, you should see something like:

```
📋 Document Information
Pages: 4        Characters Extracted: 9,812

🧠 Summary
This document discusses ... [2-5 short paragraphs]

🔑 Key Points
- Point one
- Point two
- Point three
...
```

---

## Testing the Application

You don't need a formal test framework for this project — just try the
following scenarios manually:

**Test 1 — Normal PDF**
Upload a short, text-based PDF (1-3 pages).
*Expected:* Page count and character count appear, followed by a
summary and key points within a few seconds.

**Test 2 — Multi-page / large PDF**
Upload a longer PDF (10+ pages, or paste in enough text to exceed
~12,000 characters).
*Expected:* The app still works — behind the scenes it automatically
splits the document into chunks, summarizes each chunk, and combines
them. You'll notice it takes a bit longer.

**Test 3 — Empty or scanned/image-only PDF**
Upload a PDF with no real text layer (e.g. a scanned image saved as PDF).
*Expected:* A friendly error message: *"No readable text was found in
this PDF..."* — no crash, no stack trace.

**Test 4 — Missing API key**
Rename/remove your `.env` file (or clear `GEMINI_API_KEY`) and try to
summarize a document.
*Expected:* A friendly error message asking you to set up your API key
in `.env` — the app does not crash.

**Test 5 — Invalid file**
Try uploading a non-PDF file renamed to `.pdf`, or a corrupted PDF.
*Expected:* A friendly "This file could not be read as a PDF" message.

---

## Error Handling Summary

| Situation                        | What the app does                                   |
|-----------------------------------|------------------------------------------------------|
| No file uploaded                  | "Summarize" button stays disabled / shows a warning  |
| Invalid / corrupted PDF           | Friendly error, no crash                              |
| Empty PDF / no extractable text   | Friendly error explaining why                         |
| Very large document               | Automatically chunked and summarized in parts         |
| Missing `GEMINI_API_KEY`          | Friendly error explaining how to fix it in `.env`     |
| LLM / network / CrewAI failure    | Friendly error, technical details hidden in an expander |

---

## Future Improvements

- Support for `.docx` and `.txt` uploads in addition to PDF
- OCR support for scanned/image-only PDFs
- Multiple agents (e.g. a separate "Fact Checker" agent) for more advanced pipelines
- Downloadable summary (as `.txt` or `.pdf`)
- Support for additional LLM providers (Anthropic, Gemini, local models via Ollama)
- Caching results so re-summarizing the same file is instant

---

## Author

Built by **Arun Abishek** as part of an internship learning exercise on
CrewAI and multi-agent AI systems.

---

## Git / GitHub Setup

To upload this project to your own GitHub repository, run:

```bash
git init
git add .
git commit -m "Initial CrewAI document summarizer"
git branch -M main
git remote add origin <MY_REPOSITORY_URL>
git push -u origin main
```

Replace `<MY_REPOSITORY_URL>` with your actual repository URL (e.g. from
GitHub, after creating a new empty repository).

Your `.env` file (with your real API key) is **excluded automatically**
via `.gitignore` and will not be uploaded.

# 📄 Project Documentation Generator

> **AI-powered tool that generates complete, professionally formatted final-year project reports (Black Book / Synopsis / Thesis) as Word documents — from a simple form submission.**

[![Python 3.13+](https://img.shields.io/badge/Python-3.13%2B-blue.svg)](#prerequisites)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B.svg)](#tech-stack)
[![Anthropic Claude](https://img.shields.io/badge/LLM-Anthropic%20Claude-6B46C1.svg)](#anthropic-api-setup)
[![LangGraph](https://img.shields.io/badge/Pipeline-LangGraph-4CAF50.svg)](#pipeline-architecture)

---

## Table of Contents

| #  | Section | What You'll Learn |
|----|---------|-------------------|
| 1  | [Project Overview](#1-project-overview) | What the tool does and who it's for |
| 2  | [Tech Stack](#2-tech-stack) | All frameworks, libraries, and services used |
| 3  | [Architecture & Pipeline](#3-architecture--pipeline) | How the 7-node LangGraph state machine works end-to-end |
| 4  | [File-by-File Deep Dive](#4-file-by-file-deep-dive) | Every file explained — functions, classes, constants, and logic |
| 5  | [Configuration Reference](#5-configuration-reference) | All settings, environment variables, and formatting constants |
| 6  | [Setup & Installation](#6-setup--installation) | Step-by-step instructions to get the project running |
| 7  | [Usage Guide](#7-usage-guide) | How to use the web UI, test mode, and debug console |
| 8  | [Generated Document Structure](#8-generated-document-structure) | What the output .docx looks like — every section and its formatting |
| 9  | [Cost & Performance](#9-cost--performance) | Token usage, cost estimation, concurrency, and rate limits |
| 10 | [Testing](#10-testing) | How to verify the setup and run validation |
| 11 | [Troubleshooting](#11-troubleshooting) | Common errors and how to fix them |
| 12 | [Project Structure](#12-project-structure) | Directory tree with descriptions |

---

## 1. Project Overview

> **Overview:** This section explains what the tool does, the problem it solves, and who should use it. Read this first if you want a high-level understanding of the project before diving into technical details.

### What It Does

The **Project Documentation Generator** is an AI-powered web application that takes basic project information (title, summary, tech stack, code snippets) and automatically generates a **complete, professionally formatted Word document** (.docx) suitable for submission as a final-year project report, black book, synopsis, or thesis.

### The Problem It Solves

Students spend weeks manually writing and formatting 50–250 page project documents. This tool automates the entire process:

- **Content Generation** — AI writes every chapter (Introduction, Literature Review, System Design, Implementation, Testing, Conclusion, etc.) with academic tone and correct structure.
- **Professional Formatting** — Title page, certificate, acknowledgment, abstract, table of contents, numbered headings, code blocks with syntax highlighting, diagram placeholders, markdown tables, IEEE references, and page numbers.
- **Smart Calibration** — Automatically re-writes chapters that deviate >20% from their page target.
- **Real-Time Tracking** — Every LLM call, token count, cost estimate, and time duration is logged to a JSON tracking file and shown live in a debug console.

### Key Features

| Feature | Description |
|---------|-------------|
| **Up to 250 pages** | Generates documents from 10 to 250 pages with smart page allocation |
| **Parallel LLM Calls** | All chapters are generated concurrently (12 parallel calls by default) |
| **Content Calibration** | Chapters >20% off their word target are automatically re-generated |
| **Academic Formatting** | Times New Roman, 1.5 line spacing, A4 page, proper headings, code blocks, tables |
| **Auto Table of Contents** | Uses Word field codes — right-click → Update Field in Word to populate |
| **IEEE References** | Generates 15–25 realistic IEEE-format references |
| **Diagram Placeholders** | Bordered boxes where the user can insert their own diagrams |
| **Code Blocks** | Formatted in Consolas font with gray background in a bordered table cell |
| **Live Debug Console** | Real-time log output during generation showing every pipeline step |
| **Cost Tracking** | Estimates USD cost based on token usage (Anthropic pricing model) |
| **Test Mode** | One-click toggle fills all form fields with sample data for quick testing |
| **Job History** | Sidebar shows the 5 most recent generation jobs with status |

---

## 2. Tech Stack

> **Overview:** This section lists every technology, library, and service the project depends on. Read this if you need to understand the technology choices, check compatibility, or plan infrastructure.

### Core Technologies

| Technology | Version | Purpose |
|-----------|---------|---------|
| **Python** | 3.13+ | Runtime language |
| **Streamlit** | 1.41.1 | Web UI framework — form inputs, progress bars, download buttons |
| **LangGraph** | 0.2.68 | State machine pipeline orchestration — defines the 7-node document generation graph |
| **LangChain** | 0.3.17 | LLM abstraction layer — message formatting, async invocation |
| **langchain-anthropic** | 0.3.22 | Anthropic Claude integration via `ChatAnthropic` |
| **langchain-core** | 0.3.83 | Core primitives: `HumanMessage`, `SystemMessage` |
| **Anthropic Claude** | claude-sonnet-4-6 / claude-haiku-4-5-20251001 | LLM service — dual-model strategy: Sonnet for planning, Haiku for generation |
| **python-docx** | 1.1.2 | Word document generation and formatting |
| **tiktoken** | 0.8.0 | Token counting for cost estimation |
| **nest_asyncio** | 1.6.0 | Allows `asyncio.run()` inside Streamlit's running event loop |
| **pydantic** | 2.10.6 | Data validation (used by LangChain internally) |
| **aiofiles** | 24.1.0 | Async file operations (LangGraph dependency) |
| **python-dotenv** | 1.0.1 | Loads `.env` file for API keys and model configuration |
| **langgraph-checkpoint** | 2.1.2 | LangGraph state checkpointing (dependency) |

### External Services

| Service | Details |
|---------|---------|
| **Anthropic Claude API** | API key configured via `ANTHROPIC_API_KEY` env var. Planner model: `claude-sonnet-4-6`. Generator model: `claude-haiku-4-5-20251001`. Both overridable via `.env`. |

---

## 3. Architecture & Pipeline

> **Overview:** This section explains the system architecture and the 7-step LangGraph pipeline that orchestrates document generation. Read this if you want to understand the data flow, state management, or how the pipeline processes a request from start to finish.

### High-Level Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                        STREAMLIT WEB UI (app.py)                       │
│  Form Inputs → Validation → Thread(run_pipeline) → Poll Logs → Result │
└───────────────────────────┬────────────────────────────────────────────┘
                            │
                ┌───────────▼───────────┐
                │   LangGraph Pipeline  │
                │    (pipeline.py)      │
                │   7-Node State Graph  │
                └───────────┬───────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
   ┌────▼─────┐      ┌─────▼──────┐     ┌──────▼──────┐
   │ Planner  │      │  Content   │     │  Document   │
   │(planner) │      │ Generator  │     │  Formatter  │
   │   .py    │      │   .py      │     │   .py       │
   └────┬─────┘      └─────┬──────┘     └──────┬──────┘
        │                   │                   │
   ┌────▼───────────────────▼───────────────────▼─────┐
   │               LLM Client (llm_client.py)         │
   │     sync / async / batch calls → Anthropic API   │
   └──────────────────────┬───────────────────────────┘
                          │
                ┌─────────▼─────────┐
                │  Process Tracker  │
                │   (tracker.py)    │
                │  JSON logs, cost, │
                │  tokens, timing   │
                └───────────────────┘
```

### Pipeline State Machine

The pipeline is a **linear LangGraph `StateGraph`** with 7 nodes connected sequentially:

```
START → analyze_input → plan_document → generate_front_matter → generate_chapters → calibrate_content → generate_references → format_document → END
```

### Pipeline Nodes — Detailed Breakdown

| # | Node | What It Does | LLM Calls | Progress % |
|---|------|-------------|-----------|------------|
| 1 | `analyze_input` | Validates user inputs, logs metadata (word counts, code length) to tracker. No LLM calls. | 0 | 10% |
| 2 | `plan_document` | Sends project info to the LLM (`PLANNER_MODEL` — claude-sonnet-4-6) with a detailed system prompt. The LLM returns a JSON document plan with chapters, sections, page allocations, word targets, and content strategy (`elaborate` / `summarize` / `balanced`). Uses dynamic `max_tokens` with a 2.0× buffer. | 1 | 25% |
| 3 | `generate_front_matter` | Generates the **Abstract** (250–300 words) and **Acknowledgment** (200–250 words) using two separate LLM calls via `GENERATOR_MODEL` (claude-haiku-4-5-20251001). | 2 | 35% |
| 4 | `generate_chapters` | Generates **all chapters in parallel** using `batch_call_llm` with a concurrency semaphore of 12. Each chapter uses `GENERATOR_MODEL` with dynamic `max_tokens` (1.5× buffer). | N (one per chapter) | 70% |
| 5 | `calibrate_content` | Checks every chapter's actual word count against its target. Chapters deviating >20% are re-generated via `GENERATOR_MODEL` with dynamic `max_tokens` (1.5× buffer) and expand/condense instructions. | 0 to N | 80% |
| 6 | `generate_references` | Generates 15–25 IEEE-format references relevant to the project's tech stack using `PLANNER_MODEL` (claude-sonnet-4-6). | 1 | 85% |
| 7 | `format_document` | Assembles everything into a `.docx` file using `python-docx`: title page, certificate, acknowledgment, abstract, TOC, list of figures/tables, all chapters (parsed from markdown), references, appendix (source code), and page numbers. | 0 | 100% |

### Pipeline State (`PipelineState`)

The state object that flows through every node is a `TypedDict` with these fields:

```python
class PipelineState(TypedDict):
    # User Inputs (from the web form)
    project_title: str
    project_summary: str
    project_code: str
    tech_stack: str
    target_pages: int
    college_format: str
    additional_info: str
    student_name: str
    roll_number: str
    college_name: str
    department: str
    guide_name: str
    year: str

    # Pipeline Data (populated by nodes)
    job_id: str
    document_plan: Optional[dict]       # JSON plan from planner
    chapters_content: Optional[list]    # List of chapter dicts
    front_matter: Optional[list]        # Abstract + acknowledgment
    references_content: Optional[str]   # IEEE references text
    output_file: Optional[str]          # Path to saved .docx

    # Status
    status: str
    error: Optional[str]
    progress_pct: int
```

### Async & Threading Strategy

- **Problem**: Streamlit runs inside an asyncio event loop, so calling `asyncio.run()` directly would crash.
- **Solution**: The project uses `nest_asyncio.apply()` at the top of `pipeline.py` to allow nested event loops. If `nest_asyncio` is unavailable, a thread-pool fallback patches `asyncio.run` to execute coroutines in a separate thread.
- **UI Responsiveness**: The pipeline runs in a `threading.Thread` (daemon) inside `app.py`. The main thread polls the tracker's logs every 1 second and updates the Streamlit debug console and progress bar.

---

## 4. File-by-File Deep Dive

> **Overview:** This section provides an exhaustive walkthrough of every source file — its purpose, all functions/classes, key constants, and how it connects to the rest of the system. Read this if you need to modify specific behavior, understand a particular module, or debug an issue in a specific file.

---

### 4.1 `config.py` — Configuration & Settings

**Purpose:** Central configuration module. Loads environment variables from `.env` and defines all app-wide constants used by every other module.

**Key Responsibilities:**
- Loads Anthropic API credentials and model names from environment variables
- Defines document formatting constants (fonts, sizes, spacing)
- Sets token limits and batch concurrency
- Provides `calculate_max_tokens()` for dynamic per-call token budgets
- Creates output and tracking directories

**Constants Reference:**

| Constant | Value | Description |
|----------|-------|-------------|
| `ANTHROPIC_API_KEY` | From `.env` | Anthropic API key |
| `PLANNER_MODEL` | `claude-sonnet-4-6` (overridable via `ANTHROPIC_PLANNER_MODEL` in `.env`) | Model used for document planning and IEEE references |
| `GENERATOR_MODEL` | `claude-haiku-4-5-20251001` (overridable via `ANTHROPIC_GENERATOR_MODEL` in `.env`) | Model used for front matter, all chapters, and calibration |
| `MAX_PAGES` | `250` | Maximum allowed pages |
| `MIN_PAGES` | `10` | Minimum allowed pages |
| `WORDS_PER_PAGE` | `300` | Approximate words per A4 page |
| `LINES_PER_PAGE` | `30` | Lines per page estimate |
| `DEFAULT_MAX_OUTPUT_TOKENS` | `4096` | Default max tokens when no word target is given |
| `MAX_OUTPUT_TOKENS_PER_CALL` | `8096` | Hard cap per LLM call |
| `MAX_INPUT_TOKENS_PER_CALL` | `128000` | Max input context window |
| `BATCH_CONCURRENCY` | `12` | Number of parallel LLM calls |
| `DEFAULT_FONT` | `Times New Roman` | Body text font |
| `HEADING1_SIZE` | `16` pt | Chapter heading font size |
| `HEADING2_SIZE` | `14` pt | Section heading font size |
| `HEADING3_SIZE` | `12` pt | Subsection heading font size |
| `BODY_SIZE` | `12` pt | Body text font size |
| `CODE_FONT` | `Consolas` | Code block font |
| `CODE_SIZE` | `10` pt | Code block font size |
| `LINE_SPACING` | `1.5` | Line spacing multiplier |
| `PAGE_MARGIN_INCHES` | `1.0` | Top, bottom, right margins |
| `OUTPUT_DIR` | `./output/` | Where generated .docx files are saved |
| `TRACKING_DIR` | `./tracking/` | Where JSON tracking files are saved |

**`calculate_max_tokens(word_target, buffer_multiplier, default)` — Dynamic Token Budget:**

```python
def calculate_max_tokens(word_target: int = 0, buffer_multiplier: float = 1.5, default: int = DEFAULT_MAX_OUTPUT_TOKENS) -> int:
```

- Formula: `tokens_needed = word_target × 1.33 × buffer_multiplier`
- Clamped between `DEFAULT_MAX_OUTPUT_TOKENS` (4096) and `MAX_OUTPUT_TOKENS_PER_CALL` (8096)
- Planner uses `buffer_multiplier=2.0`; chapters and calibration use `buffer_multiplier=1.5` (default)
- Returns `default` (4096) when `word_target <= 0`

**Imported by:** Every other module (`llm_client.py`, `tracker.py`, `planner.py`, `content_generator.py`, `doc_formatter.py`, `app.py`).

---

### 4.2 `tracker.py` — Process Tracking System

**Purpose:** Logs every step of the document generation pipeline — token usage, timing, costs, status changes, and live debug messages — and persists everything to a JSON file.

**Class: `ProcessTracker`**

| Method | Signature | Description |
|--------|-----------|-------------|
| `__init__` | `(job_id: str)` | Creates tracker, initializes JSON structure, records start time |
| `log` | `(message: str)` | Appends a timestamped `[elapsed_seconds] message` line for live debug output |
| `get_logs` | `() -> list[str]` | Returns all accumulated log lines |
| `set_status` | `(status: str)` | Updates overall job status and saves |
| `set_user_inputs` | `(inputs: dict)` | Stores the user's form data in tracking JSON |
| `set_document_plan` | `(plan: dict)` | Stores the generated document plan/outline |
| `start_step` | `(step_name, description) -> str` | Begins tracking a new step, returns `step_id` |
| `complete_step` | `(step_id, input_tokens, output_tokens, llm_calls, status)` | Records step completion with token counts and duration |
| `fail_step` | `(step_id, error)` | Records step failure with error message |
| `complete_job` | `(output_file)` | Marks entire job complete, records output file path |
| `fail_job` | `(error)` | Marks entire job as failed |
| `get_progress` | `() -> dict` | Returns progress summary: `{job_id, status, progress, progress_pct, current_step, total_tokens, cost_usd, duration_seconds}` |
| `load` | `() -> dict` | Reloads tracking data from the JSON file |

**JSON Tracking File Structure** (saved to `tracking/doc_YYYYMMDD_HHMMSS.json`):

```json
{
  "job_id": "doc_20260212_232509",
  "status": "completed",
  "started_at": "2026-02-12T23:25:09",
  "completed_at": "2026-02-12T23:28:15",
  "user_inputs": { ... },
  "document_plan": { ... },
  "total_tokens": { "input": 45000, "output": 32000, "total": 77000 },
  "cost_estimate_usd": 0.4325,
  "total_duration_seconds": 186.42,
  "steps": [
    {
      "step_id": "step_1",
      "step_name": "input_analysis",
      "status": "completed",
      "started_at": "...",
      "completed_at": "...",
      "duration_seconds": 0.01,
      "tokens": { "input": 0, "output": 0, "total": 0 },
      "llm_calls": 0
    }
  ],
  "errors": []
}
```

**Cost Estimation Formula:**
- Input tokens: `$2.50 / 1M tokens`
- Output tokens: `$10.00 / 1M tokens`
- Used as an approximation; see Section 9 for Anthropic-specific pricing.

---

### 4.3 `llm_client.py` — Anthropic Claude LLM Client

**Purpose:** Provides synchronous, asynchronous, and batch-parallel interfaces for calling Anthropic Claude, with automatic token counting.

**Functions:**

| Function | Signature | Description |
|----------|-----------|-------------|
| `get_llm` | `(temperature=0.7, max_tokens=DEFAULT_MAX_OUTPUT_TOKENS, model=None) -> ChatAnthropic` | Creates and returns a configured `ChatAnthropic` instance. Uses `GENERATOR_MODEL` when `model` is `None`. API key and model are sourced from `config.py`. |
| `count_tokens` | `(text: str, model="gpt-4o") -> int` | Counts tokens using `tiktoken`. Falls back to `cl100k_base` encoding if the model is not recognized |
| `call_llm` | `(system_prompt, user_prompt, temperature=0.7, max_tokens=DEFAULT_MAX_OUTPUT_TOKENS, model=None) -> dict` | **Synchronous** LLM call. Returns `{content, input_tokens, output_tokens}`. Pass `model=PLANNER_MODEL` to use Sonnet. |
| `call_llm_async` | `(system_prompt, user_prompt, temperature=0.7, max_tokens=DEFAULT_MAX_OUTPUT_TOKENS, model=None) -> dict` | **Asynchronous** LLM call using `llm.ainvoke()`. Same return format |
| `batch_call_llm` | `(calls: list[dict], concurrency=5) -> list[dict]` | Runs multiple async LLM calls in parallel, gated by an `asyncio.Semaphore(concurrency)`. Each item in `calls` is `{system_prompt, user_prompt, temperature?, max_tokens?, model?}`. Errors are caught per-call and returned as `{content: "ERROR: ...", error: "..."}` |

**Key Implementation Details:**
- `batch_call_llm` uses `asyncio.gather(*tasks, return_exceptions=True)` so one failed call doesn't abort the entire batch.
- The `ChatAnthropic` instance is created fresh for each call (stateless).
- The `model` parameter in all functions defaults to `None`, which resolves to `GENERATOR_MODEL` inside `get_llm()`. Callers that need the planner model explicitly pass `model=PLANNER_MODEL`.
- Token counting uses `tiktoken.encoding_for_model("gpt-4o")` with a `cl100k_base` fallback (used as an approximation for Anthropic models).

---

### 4.4 `planner.py` — Document Planner

**Purpose:** Takes user inputs and uses the LLM (`PLANNER_MODEL` — claude-sonnet-4-6) to create a structured JSON document plan — the blueprint that drives all subsequent content generation. Uses `calculate_max_tokens()` with a 2.0× buffer to ensure the full plan JSON fits in a single response.

**Function:**

| Function | Signature | Description |
|----------|-----------|-------------|
| `create_document_plan` | `(project_title, project_summary, project_code, tech_stack, target_pages, college_format, additional_info, tracker) -> dict` | Sends a detailed prompt to the LLM requesting a JSON document plan. Uses regex-based code fence stripping (handles ` ```json `, ` ```JSON `, ` ``` `, and surrounding text) and then falls back to a `{...}` regex extraction before `json.loads()`. Returns the plan dict. |

**System Prompt Rules** (from `PLANNER_SYSTEM_PROMPT`):
1. Total pages must equal the user's requested page count
2. Pages are distributed: front matter + chapters + back matter = total pages
3. Content strategy is automatically set: `elaborate` (user info < needed), `summarize` (user info > needed), or `balanced`
4. Diagram placeholders are included where appropriate (system architecture, ER diagram, DFD, flowchart, use case, class diagram, sequence diagram)
5. Standard chapter structure: Introduction, Literature Review, System Requirements & Analysis, System Design, Implementation, Testing, Results & Discussion, Conclusion & Future Scope
6. Chapters can be added/modified based on project type

**Document Plan JSON Schema:**

```json
{
  "title": "Project Title",
  "document_type": "Black Book / Synopsis / Thesis",
  "chapters": [
    {
      "chapter_number": 1,
      "title": "Introduction",
      "page_allocation": 10,
      "word_target": 3000,
      "sections": [
        {
          "section_number": "1.1",
          "title": "Background",
          "description": "Brief description...",
          "has_code": false,
          "has_diagram_placeholder": false,
          "diagram_type": null
        }
      ]
    }
  ],
  "front_matter": [
    {"type": "title_page", "page_allocation": 1},
    {"type": "certificate", "page_allocation": 1},
    {"type": "acknowledgment", "page_allocation": 1},
    {"type": "abstract", "page_allocation": 2},
    {"type": "table_of_contents", "page_allocation": 2},
    {"type": "list_of_figures", "page_allocation": 1},
    {"type": "list_of_tables", "page_allocation": 1}
  ],
  "back_matter": [
    {"type": "references", "page_allocation": 3},
    {"type": "appendix", "page_allocation": 10}
  ],
  "content_strategy": "elaborate",
  "total_content_pages": 40,
  "total_pages": 60
}
```

**Page Allocation Logic:**
- Front matter estimate: 9 pages (title + certificate + acknowledgment + abstract + TOC + list of figures + list of tables)
- Back matter estimate: `max(5, target_pages * 5%)`
- Content pages: `target_pages - front_matter - back_matter`

---

### 4.5 `content_generator.py` — Chapter & Front Matter Generator

**Purpose:** Generates all chapter content in parallel using batch LLM calls, generates front matter (abstract & acknowledgment), and calibrates content to hit word targets. All LLM calls in this module use `GENERATOR_MODEL` (claude-haiku-4-5-20251001) with dynamic `max_tokens` calculated via `calculate_max_tokens()`.

**Functions:**

| Function | Signature | Description |
|----------|-----------|-------------|
| `generate_front_matter` | `(section_type, project_title, project_summary, student_name, college_name, guide_name, department, year, tracker) -> dict` | Generates either `abstract` (250–300 words) or `acknowledgment` (200–250 words) using `GENERATOR_MODEL`. Returns `{type, content}` |
| `generate_all_chapters` | `async (plan, project_summary, project_code, tech_stack, additional_info, tracker) -> list[dict]` | Generates all chapters in parallel using `batch_call_llm`. Each chapter uses `GENERATOR_MODEL` with `calculate_max_tokens(chapter["word_target"])` (1.5× buffer). Returns list of `{chapter_number, title, content, word_count, target_words, sections}` |
| `calibrate_content` | `async (chapters, plan, tracker) -> list[dict]` | Checks each chapter's word count vs target. If deviation >20%, re-generates with `GENERATOR_MODEL` and `calculate_max_tokens(target)` (1.5× buffer) using expand/condense instructions. Returns the updated chapters list |

**System Prompts:**

- `CHAPTER_SYSTEM_PROMPT` — Instructs the LLM to write academic content with:
  - Formal, third-person tone
  - Exact word count matching
  - `##` for sections, `###` for subsections
  - Code blocks in triple backticks
  - Diagram placeholders as `[DIAGRAM: type - description]`
  - Markdown tables
  - 4–6 sentence paragraphs
  - Transitional phrases between sections

- `FRONT_MATTER_SYSTEM_PROMPT` — Instructs the LLM to generate formal academic front matter content

**Calibration Logic:**
1. For each chapter, compute `deviation = |actual_words - target_words| / target_words`
2. If `deviation > 0.20` (20%):
   - If under target → expand with more detail, examples, explanations
   - If over target → condense, keeping most important points
3. Re-generation calls are batched and run in parallel

---

### 4.6 `doc_formatter.py` — Word Document Formatter

**Purpose:** Assembles all generated content into a professionally formatted `.docx` file using `python-docx`. This is the largest file in the project (747 lines) and handles every aspect of document formatting.

**Class: `DocumentFormatter`**

| Method | Description |
|--------|-------------|
| `__init__(filename)` | Creates a new Word document, sets up custom styles and A4 page layout |
| `_setup_page_layout()` | Configures A4 page size (8.27" × 11.69"), margins (1.25" left, 1.0" others) |
| `_setup_styles()` | Defines Normal (justified), Heading 1/2/3, and Code paragraph styles with fonts and sizes |
| `add_title_page(...)` | Adds formatted title page: college name, department, project title, student info, guide, year |
| `add_certificate_page(...)` | Adds certificate with body text and signature table (Guide, HOD, External Examiner) |
| `add_acknowledgment(content)` | Adds acknowledgment section with centered title |
| `add_abstract(content)` | Adds abstract section with centered title |
| `add_table_of_contents()` | Inserts a Word TOC field code (`TOC \o "1-3" \h \z \u`) — auto-updates when user right-clicks in Word |
| `add_list_of_figures()` | Adds a placeholder page for figure index |
| `add_list_of_tables()` | Adds a placeholder page for table index |
| `add_chapter(chapter_number, title, content)` | Adds full chapter with Heading 1 title, then parses content through `_parse_and_add_content()` |
| `add_references(content)` | Adds References section as Heading 1 with formatted content |
| `add_appendix(content)` | Adds Appendix section — defaults to source code |
| `add_page_numbers()` | Inserts PAGE field codes in every section footer |
| `save() -> str` | Saves document to `OUTPUT_DIR/{filename}`, returns absolute path |

**Content Parser — `_parse_and_add_content(content, chapter_number)`**

This method processes LLM-generated markdown-like content line by line and converts it to Word formatting:

| Pattern | Handling |
|---------|----------|
| ` ```lang ... ``` ` | Wrapped in a single-cell table with gray `#F5F5F5` background, Consolas font |
| `[DIAGRAM: type - desc]` | Bordered box placeholder (5.5" wide) with gray instruction text and auto-numbered figure caption |
| `\| col \| col \|` (markdown table) | Converted to a Word table with header row (blue `#D9E2F3` background) and borders |
| `## Heading` | Heading level 2 |
| `### Heading` | Heading level 3 |
| `- item` or `* item` | List Bullet style |
| `1. item` | List Number style |
| `**bold**` | Bold run |
| `*italic*` | Italic run |
| Regular text | Normal paragraph with 1.5 line spacing, justified alignment |

**Diagram Placeholder Details:**
- Created as a bordered single-cell table (5.5" wide)
- 8 empty lines above and below the center text for visual space
- Center text: `[Insert {diagram_type} Here]` in gray italic
- Auto-captioned: `Figure {chapter}.{figure_count}: {diagram_type}`
- Figure counter increments across the entire document

**Code Block Details:**
- Rendered as a single-cell table with `#F5F5F5` (light gray) background shading
- Font: Consolas 10pt with 1.0 line spacing
- Border: light gray `#CCCCCC` single-line
- Language label displayed above the code block

---

### 4.7 `pipeline.py` — LangGraph Pipeline Orchestrator

**Purpose:** Defines the LangGraph `StateGraph` with 7 nodes, manages the global tracker registry, and provides the main `run_pipeline()` entry point that the UI calls. Imports both `PLANNER_MODEL` and `GENERATOR_MODEL` from `config.py` to log which model is being used at each stage.

**Key Components:**

**Async Patch (top of file):**
```python
try:
    import nest_asyncio
    nest_asyncio.apply()
except ImportError:
    # Fallback: ThreadPoolExecutor-based asyncio.run patch
```

**Global Tracker Registry:**
```python
_trackers: dict[str, ProcessTracker] = {}

def get_tracker(job_id: str) -> ProcessTracker:
    """Get or create a tracker for the given job ID."""
```
This registry is also accessed by `app.py` to poll live logs from the background thread.

**Node Functions:** Each node function takes a `PipelineState` dict and returns a partial dict that LangGraph merges into the state. See [Pipeline Nodes — Detailed Breakdown](#pipeline-nodes--detailed-breakdown) above for the complete table.

Notable model usage per node:
- `plan_document_node` — logs `PLANNER_MODEL` and calls `create_document_plan()` (uses Sonnet)
- `generate_chapters_node` — logs `GENERATOR_MODEL` (Haiku) for batch chapter generation
- `generate_references_node` — explicitly passes `model=PLANNER_MODEL` (Sonnet) to `call_llm()`

**Graph Construction — `build_pipeline()`:**
```python
graph = StateGraph(PipelineState)
graph.add_node("analyze_input", analyze_input_node)
graph.add_node("plan_document", plan_document_node)
# ... (7 nodes total)
graph.add_edge(START, "analyze_input")
graph.add_edge("analyze_input", "plan_document")
# ... (linear chain to END)
return graph.compile()
```

**Entry Point — `run_pipeline(...) -> dict`:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `project_title` | `str` | required | Project title |
| `project_summary` | `str` | required | Detailed project description |
| `project_code` | `str` | `""` | Source code (optional) |
| `tech_stack` | `str` | `""` | Technologies used |
| `target_pages` | `int` | `50` | Target page count |
| `college_format` | `str` | `""` | College-specific format requirements |
| `additional_info` | `str` | `""` | Extra context |
| `student_name` | `str` | `"Student Name"` | Student name for title/certificate |
| `roll_number` | `str` | `"000"` | Roll number |
| `college_name` | `str` | `"University"` | College name |
| `department` | `str` | `"Department of Computer Science"` | Department |
| `guide_name` | `str` | `"Prof. Guide"` | Guide/mentor name |
| `year` | `str` | `"2025-2026"` | Academic year |

**Return Value:**
```python
{
    "job_id": "doc_20260212_232509",
    "status": "completed",         # or "failed"
    "output_file": "/path/to/output/doc_xxx.docx",
    "tracking_file": "/path/to/tracking/doc_xxx.json",
    "total_tokens": {"input": ..., "output": ..., "total": ...},
    "cost_usd": 0.4325,
    "duration_seconds": 186.42,
    "logs": ["[  0.0s] 🚀 Pipeline started", ...]
}
```

---

### 4.8 `app.py` — Streamlit Web Interface

**Purpose:** Provides the complete web UI — form inputs, validation, threaded pipeline execution with live log polling, progress display, results, and document download.

**Key Sections:**

**1. Custom CSS** — Defines gradient header, card styles, step-tracker colors (green/yellow/red/gray)

**2. Session State:**
- `generation_started` — Boolean flag for UI state switching
- `result` — Pipeline result dict (or `None`)
- `job_id` — Current job identifier

**3. Test Data (`_TEST_DATA` dict):**

A comprehensive sample project ("Smart Attendance System using Face Recognition") with:
- Title, summary (170+ words describing a face-recognition attendance system)
- Tech stack: `Python, OpenCV, Flask, SQLite, HTML/CSS, JavaScript`
- Additional info: database schema, API endpoints, face recognition thresholds
- Sample Flask code (~30 lines)
- Student info: name, roll number, college, department, guide, year

The toggle `🧪 Auto-fill Test Data` in the sidebar conditionally populates every form field with `_TEST_DATA` values using ternary expressions: `value=_TEST_DATA["field"] if test_mode else ""`.

**4. Sidebar:**
- Test mode toggle
- "How it Works" — 5-step workflow
- "Capabilities" — feature list with checkmarks
- "Previous Jobs" — loads the 5 most recent JSON tracking files from `TRACKING_DIR`, shows job ID with status emoji

**5. Main Form (2 tabs):**

**Tab 1 — Project Details:**
- Project Title (text input, required)
- Technology Stack (text input, required)
- Target Pages (slider, 10–250, step 5, default 60)
- Project Summary (text area, 200px height, required, min 20 words)
- Additional Information (text area, optional)
- Code Upload (radio: Paste Code / Upload File / No Code)
  - Paste: text area with 300px height
  - Upload: file uploader supporting `.py, .js, .ts, .java, .cpp, .c, .html, .css, .jsx, .tsx, .php, .rb, .go, .rs, .kt`
- College Format Template (text area, optional)

**Tab 2 — Student & College Info:**
- Student Name, Roll Number, College Name, Department, Guide Name, Academic Year

**6. Generation Flow:**
1. Validation: title, summary, tech stack must be non-empty; summary must be ≥20 words
2. Inputs stored in `st.session_state.inputs`
3. `st.session_state.generation_started = True` → `st.rerun()`
4. Second render: pipeline runs in `threading.Thread(target=_run, daemon=True)`
5. Main thread polls `tracker.get_logs()` every 1 second
6. Logs displayed in `st.code(log_text, language="text")` — terminal-style monospaced block
7. Progress bar updated from `tracker.get_progress()["progress_pct"]`
8. On completion: `st.session_state.result = pipeline_result[0]` → `st.rerun()`

**7. Results Display:**
- Success banner with 4 metrics: Status, Total Tokens, Cost (USD), Duration
- Download button for the `.docx` file
- Expandable tracking details (raw JSON + step-by-step breakdown with colored cards)
- Expandable debug console log
- "Generate Another Document" reset button

---

### 4.9 `test_project.py` — Import Verification

**Purpose:** Validates that all 13 required imports work correctly. Not a unit test suite — it's a setup verification script.

**Tests (13 total):**
1. `config` — `ANTHROPIC_API_KEY, OUTPUT_DIR, TRACKING_DIR`
2. `tracker` — `ProcessTracker`
3. `llm_client` — `get_llm, call_llm, count_tokens, batch_call_llm`
4. `planner` — `create_document_plan`
5. `content_generator` — `generate_all_chapters, generate_front_matter, calibrate_content`
6. `doc_formatter` — `DocumentFormatter`
7. `pipeline` — `run_pipeline, build_pipeline`
8. `python-docx` — `Document`
9. `streamlit` — `streamlit`
10. `tiktoken` — `tiktoken`
11. `langgraph` — `StateGraph, START, END`
12. `langchain-anthropic` — `ChatAnthropic`
13. `langchain-core` — `HumanMessage, SystemMessage`

**Run:** `python test_project.py`

---

### 4.10 `requirements.txt` — Python Dependencies

```
langchain==0.3.17
langchain-anthropic==0.3.22
langchain-core==0.3.83
langgraph==0.2.68
langgraph-checkpoint==2.1.2
python-dotenv==1.0.1
python-docx==1.1.2
streamlit==1.41.1
aiofiles==24.1.0
pydantic==2.10.6
tiktoken==0.8.0
nest_asyncio==1.6.0
```

**Note:** `langchain-core` is pinned to `0.3.83` (exact version) to ensure compatibility with `langchain==0.3.17` and `langchain-anthropic==0.3.22`. `langchain-openai` has been removed and replaced with `langchain-anthropic`.

---

## 5. Configuration Reference

> **Overview:** This section is a quick-reference for all configurable values — environment variables, document formatting, token limits, and file paths. Read this if you want to customize the output formatting, switch models, or change operational parameters.

### Environment Variables (`.env` file)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | Yes | — | Anthropic API key (get it from [console.anthropic.com](https://console.anthropic.com)) |
| `ANTHROPIC_PLANNER_MODEL` | No | `claude-sonnet-4-6` | Model used for document planning and IEEE reference generation. Override to use a different Sonnet variant. |
| `ANTHROPIC_GENERATOR_MODEL` | No | `claude-haiku-4-5-20251001` | Model used for front matter, all chapter generation, and calibration. Override to use a different Haiku variant. |

### Model Settings

| Role | Default Model | Used For | Override Variable |
|------|--------------|----------|-------------------|
| **Planner** | `claude-sonnet-4-6` | Document planning (node 2), IEEE references (node 6) | `ANTHROPIC_PLANNER_MODEL` |
| **Generator** | `claude-haiku-4-5-20251001` | Front matter (node 3), all chapters (node 4), calibration (node 5) | `ANTHROPIC_GENERATOR_MODEL` |

The planner uses the more capable Sonnet model for structured reasoning (JSON plan generation). The generator uses the faster, cheaper Haiku model for bulk text generation where throughput matters more than complex reasoning.

### Document Formatting Constants (in `config.py`)

| Setting | Value | Customization Notes |
|---------|-------|---------------------|
| Font | Times New Roman 12pt | Change `DEFAULT_FONT` and `BODY_SIZE` |
| Headings | 16pt / 14pt / 12pt | Change `HEADING1_SIZE`, `HEADING2_SIZE`, `HEADING3_SIZE` |
| Code | Consolas 10pt | Change `CODE_FONT`, `CODE_SIZE` |
| Line Spacing | 1.5× | Change `LINE_SPACING` |
| Body Text Alignment | Justified | Applied to Normal style and body paragraphs in `doc_formatter.py` |
| Page Size | A4 (8.27" × 11.69") | Hardcoded in `doc_formatter.py` |
| Margins | 1.25" left, 1.0" top/bottom/right | Left margin hardcoded, others via `PAGE_MARGIN_INCHES` |
| Words/Page | 300 | Change `WORDS_PER_PAGE` — affects page allocation math |

### Operational Settings (in `config.py`)

| Setting | Value | Notes |
|---------|-------|-------|
| `BATCH_CONCURRENCY` | `12` | Parallel LLM calls. Anthropic Claude API supports high concurrency — adjust if hitting rate limits. |
| `DEFAULT_MAX_OUTPUT_TOKENS` | `4096` | Fallback token budget when no word target is given |
| `MAX_OUTPUT_TOKENS_PER_CALL` | `8096` | Hard cap per LLM call — `calculate_max_tokens()` never exceeds this |
| `MAX_INPUT_TOKENS_PER_CALL` | `128000` | Model context window |
| `MAX_PAGES` | `250` | UI slider upper bound |
| `MIN_PAGES` | `10` | UI slider lower bound |

---

## 6. Setup & Installation

> **Overview:** Step-by-step instructions to set up the project from scratch. Read this if you're setting up the project for the first time or on a new machine.

### Prerequisites

- **Python 3.13+** installed and on your PATH
- **Anthropic API key** (sign up at [console.anthropic.com](https://console.anthropic.com))
- **Git** (optional, for cloning)

### Step 1: Clone or Download

```bash
git clone <repository-url>
cd project-document-agent
```

### Step 2: Create Virtual Environment

```bash
python -m venv myenv
```

**Activate:**
- **Windows (PowerShell):** `.\myenv\Scripts\Activate.ps1`
- **Windows (CMD):** `myenv\Scripts\activate.bat`
- **Linux/Mac:** `source myenv/bin/activate`

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the project root:

```env
# Required
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Optional — override default model selections
ANTHROPIC_PLANNER_MODEL=claude-sonnet-4-6
ANTHROPIC_GENERATOR_MODEL=claude-haiku-4-5-20251001
```

> **How to get your API key:**
> 1. Go to [console.anthropic.com](https://console.anthropic.com)
> 2. Sign in or create an account
> 3. Navigate to **API Keys** → **Create Key**
> 4. Copy the key and paste it as `ANTHROPIC_API_KEY` in your `.env` file

### Step 5: Verify Setup

```bash
python test_project.py
```

Expected output:
```
Python: 3.13.x ...

  ✓ config
  ✓ tracker
  ✓ llm_client
  ✓ planner
  ✓ content_generator
  ✓ doc_formatter
  ✓ pipeline
  ✓ python-docx
  ✓ streamlit
  ✓ tiktoken
  ✓ langgraph
  ✓ langchain-anthropic
  ✓ langchain-core

========================================
Results: 13 passed, 0 failed

✅ All imports working! Project is ready.
```

### Step 6: Launch the Application

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`.

---

## 7. Usage Guide

> **Overview:** This section walks you through using the web interface — filling the form, using test mode, understanding the debug console, and downloading the result. Read this if you want to know how to actually use the tool.

### Normal Usage

1. Open `http://localhost:8501` in your browser
2. **Tab 1 — Project Details:**
   - Enter your project title
   - Enter the technology stack
   - Set the target page count (slider)
   - Write a detailed project summary (the more detail, the better the output)
   - Optionally add extra info, code, and college format requirements
3. **Tab 2 — Student & College Info:**
   - Fill in student name, roll number, college, department, guide, and year
4. Click **🚀 Generate Documentation**
5. Watch the live debug console for real-time progress
6. When complete, click **📥 Download Your Document (.docx)**

### Test Mode (Quick Testing)

1. Enable the **🧪 Auto-fill Test Data** toggle in the sidebar
2. All fields auto-populate with a sample project: "Smart Attendance System using Face Recognition"
3. Click **🚀 Generate Documentation** to test the full pipeline without typing anything

### Understanding the Debug Console

During generation, you'll see timestamped logs like:

```
[    0.0s] 🚀 Pipeline started
[    0.0s]    Job ID: doc_20260212_232509
[    0.1s] 🔍 Starting input analysis...
[    0.1s]    Project: Smart Attendance System using Face Recognition
[    0.1s]    Target pages: 60
[    0.1s] ✅ Input analysis complete
[    3.2s] 📝 Planning document structure (model: claude-sonnet-4-6)...
[    8.5s] ✅ Document plan created: 8 chapters
[    8.5s]    Ch 1: Introduction (8 pages, 2400 words)
[    8.5s]    Ch 2: Literature Review (7 pages, 2100 words)
...
```

### After Generation — Results

- **4 metrics** displayed: Status, Total Tokens, Cost (USD), Duration
- **Download button** for the `.docx` file
- **Tracking Details** (expandable): Full JSON tracking data + step breakdown
- **Debug Console Log** (expandable): Complete log from start to finish

---

## 8. Generated Document Structure

> **Overview:** This section describes exactly what the output Word document contains and how it's formatted. Read this if you want to know what pages are included, how code/diagrams/tables look, or what academic structure is followed.

### Document Sections (in order)

| # | Section | Pages | Description |
|---|---------|-------|-------------|
| 1 | **Title Page** | 1 | College name (uppercase, 18pt bold), department, "A Project Report On", project title (18pt bold, blue), student name, roll number, guide name, academic year — all centered |
| 2 | **Certificate** | 1 | Formal certification text (justified), signature table with 3 columns: Project Guide, Head of Department, External Examiner |
| 3 | **Acknowledgment** | 1 | LLM-generated formal acknowledgment (200–250 words) |
| 4 | **Abstract** | 1–2 | LLM-generated abstract (250–300 words) covering background, problem, methodology, features, tech, conclusion |
| 5 | **Table of Contents** | 1–2 | Word field code — right-click → "Update Field" in Microsoft Word to auto-populate |
| 6 | **List of Figures** | 1 | Placeholder page |
| 7 | **List of Tables** | 1 | Placeholder page |
| 8 | **Chapters** | Variable | Each chapter starts with Heading 1 (`Chapter N: Title`), followed by parsed content with sections, code blocks, diagram placeholders, tables, lists |
| 9 | **References** | 2–3 | 15–25 IEEE-format references generated by LLM |
| 10 | **Appendix** | Variable | Source code (first 10,000 characters) or placeholder |

### Standard Chapter Lineup

The LLM planner typically creates these chapters (varies by project):

1. **Introduction** — Background, problem statement, objectives, scope, methodology overview
2. **Literature Review** — Related work, existing solutions, comparative analysis
3. **System Requirements & Analysis** — Functional/non-functional requirements, feasibility study
4. **System Design** — Architecture diagram, ER diagram, DFD, use case diagrams, class diagrams
5. **Implementation** — Code walkthroughs, module descriptions, screenshots
6. **Testing** — Test cases, unit/integration/system testing, test results
7. **Results & Discussion** — Output analysis, performance metrics, screenshots
8. **Conclusion & Future Scope** — Summary, achievements, limitations, future enhancements

---

## 9. Cost & Performance

> **Overview:** This section covers token usage, cost estimation, generation speed, and Anthropic rate limits. Read this if you want to estimate costs, optimize speed, or understand the batch processing limits.

### Token Usage Estimates

| Document Size | Approx. Input Tokens | Approx. Output Tokens | Estimated Cost* |
|--------------|----------------------|----------------------|----------------|
| 30 pages | ~30K | ~20K | ~$0.03–0.08 |
| 60 pages | ~50K | ~35K | ~$0.05–0.15 |
| 120 pages | ~80K | ~60K | ~$0.10–0.25 |
| 250 pages | ~150K | ~120K | ~$0.20–0.50 |

*Most tokens are generated by `GENERATOR_MODEL` (Haiku), with only planning and references using `PLANNER_MODEL` (Sonnet). Costs are approximations based on the pricing below.

### Anthropic Pricing (as of early 2026)

| Model | Input (per 1M tokens) | Output (per 1M tokens) | Used For |
|-------|----------------------|------------------------|----------|
| **claude-sonnet-4-6** | ~$3.00 | ~$15.00 | Planning (node 2), References (node 6) |
| **claude-haiku-4-5-20251001** | ~$0.25 | ~$1.25 | Front matter (node 3), Chapters (node 4), Calibration (node 5) |

Because the vast majority of output tokens come from the Haiku model (chapter generation), the effective cost per document is significantly lower than an all-Sonnet approach.

### Generation Speed

| Document Size | Estimated Duration | With 12 Concurrency |
|--------------|-------------------|---------------------|
| 30 pages | 1–3 minutes | ~1–2 minutes |
| 60 pages | 3–6 minutes | ~2–4 minutes |
| 120 pages | 5–10 minutes | ~4–7 minutes |
| 250 pages | 8–15 minutes | ~6–10 minutes |

### Anthropic Rate Limits

Anthropic's API limits vary by tier. The current `BATCH_CONCURRENCY = 12` is appropriate for most standard API tiers. If you encounter `overloaded_error` or `rate_limit_error` responses, reduce `BATCH_CONCURRENCY` in `config.py`.

### Adjusting Concurrency

In `config.py`, change:
```python
BATCH_CONCURRENCY = 12  # Increase for faster generation, decrease if hitting rate limits
```

---

## 10. Testing

> **Overview:** This section explains how to test and verify the project setup. Read this if you want to validate your installation or run checks.

### Verify Imports

```bash
python test_project.py
```

This runs 13 import checks covering every module and dependency. All 13 should pass.

### Quick End-to-End Test

1. Launch: `streamlit run app.py`
2. Enable **🧪 Auto-fill Test Data** in the sidebar
3. Click **🚀 Generate Documentation**
4. Monitor the debug console for progress
5. Download the resulting `.docx` and open it in Microsoft Word
6. Right-click the Table of Contents → "Update Field" → "Update entire table"

### Verify Tracking

After a generation run, check `tracking/doc_YYYYMMDD_HHMMSS.json` for:
- `"status": "completed"`
- Token counts in each step
- `cost_estimate_usd` value
- No entries in `"errors": []`

---

## 11. Troubleshooting

> **Overview:** Common errors and their solutions. Read this if you encounter an issue during setup or generation.

### `AuthenticationError` — Invalid API Key

**Cause:** The `ANTHROPIC_API_KEY` in your `.env` is missing, incorrect, or has expired.

**Fix:** Get a valid key from [console.anthropic.com](https://console.anthropic.com) → API Keys, then update `.env`:
```env
ANTHROPIC_API_KEY=sk-ant-...
```

### `NotFoundError` — Model Not Found

**Cause:** The model name in `ANTHROPIC_PLANNER_MODEL` or `ANTHROPIC_GENERATOR_MODEL` does not exist or is not available on your account.

**Fix:** Remove the override from `.env` to use the tested defaults, or check [Anthropic's model documentation](https://docs.anthropic.com/en/docs/about-claude/models) for the correct model ID:
```env
# Remove these lines or correct the model IDs:
ANTHROPIC_PLANNER_MODEL=claude-sonnet-4-6
ANTHROPIC_GENERATOR_MODEL=claude-haiku-4-5-20251001
```

### `OverloadedError` or Rate Limit Errors

**Cause:** Too many parallel requests sent to the Anthropic API simultaneously.

**Fix:** Reduce `BATCH_CONCURRENCY` in `config.py`:
```python
BATCH_CONCURRENCY = 5  # Lower value reduces parallel load
```

### `RuntimeError: This event loop is already running`

**Cause:** `nest_asyncio` is not installed.

**Fix:**
```bash
pip install nest_asyncio==1.6.0
```

### `langchain-core` Version Conflict

**Cause:** `langchain-core` version conflicts with `langchain` or `langchain-anthropic`.

**Fix:** Pin to the tested version in `requirements.txt`:
```
langchain-core==0.3.83
```

### `langgraph-checkpoint==2.1.3` Installation Fails

**Cause:** Version 2.1.3 was yanked from PyPI.

**Fix:** Use version 2.1.2:
```
langgraph-checkpoint==2.1.2
```

### Generation Takes Too Long

**Possible causes and fixes:**
1. **Low concurrency** — Increase `BATCH_CONCURRENCY` in `config.py` if within rate limits
2. **High page count** — 250 pages takes 8–15 minutes; start with 30–60 pages for testing
3. **Network latency** — Ensure good connectivity to Anthropic's API endpoints
4. **Calibration overhead** — If many chapters miss their word targets, re-generation adds time

### Empty or Broken `.docx` Output

**Possible causes:**
- LLM returned error responses — check `tracking/doc_xxx.json` for errors
- Content parsing failed — look for malformed markdown in chapter content
- `python-docx` version mismatch — ensure `python-docx==1.1.2`

### Table of Contents Shows "Right-click and select 'Update Field'"

**This is expected.** Open the `.docx` in Microsoft Word → right-click the TOC → select "Update Field" → "Update entire table." The TOC uses Word field codes that populate on update.

---

## 12. Project Structure

> **Overview:** Complete directory tree with descriptions. Read this for a quick map of the entire project.

```
project-document-agent/
│
├── app.py                  # Streamlit web UI — forms, progress, download
├── pipeline.py             # LangGraph 7-node state machine pipeline
├── planner.py              # LLM-based document structure planner (uses PLANNER_MODEL)
├── content_generator.py    # Parallel chapter generation + calibration (uses GENERATOR_MODEL)
├── doc_formatter.py        # python-docx Word document builder (747 lines)
├── llm_client.py           # Anthropic Claude sync/async/batch client
├── tracker.py              # Process tracking — tokens, timing, costs, logs
├── config.py               # All settings, constants, env vars, calculate_max_tokens()
├── test_project.py         # Import verification script (13 checks)
├── requirements.txt        # Python dependencies (12 packages)
├── .env                    # Anthropic API key and optional model overrides (not committed)
├── README.md               # This file
│
├── output/                 # Generated .docx files
│   └── doc_YYYYMMDD_HHMMSS.docx
│
├── tracking/               # JSON tracking files per job
│   └── doc_YYYYMMDD_HHMMSS.json
│
└── myenv/                  # Python virtual environment
    ├── Scripts/            # Activation scripts (Windows)
    └── Lib/site-packages/  # Installed packages
```

---

## License

This project is intended for educational purposes. Use responsibly.

---

*Built with Python, Streamlit, LangGraph, LangChain, Anthropic Claude, and python-docx.*

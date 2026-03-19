# Project Documentation Generator - Complete Flow Diagram

## 1. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         STREAMLIT WEB APPLICATION                           │
│                              (app.py)                                       │
│                                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  Form Inputs │  │ Sidebar Info │  │  Test Mode   │  │ Job History  │   │
│  │              │  │              │  │              │  │              │   │
│  │ - Project    │  │ - How Works  │  │ - Auto-fill  │  │ - 5 Recent   │   │
│  │   Title      │  │ - Features   │  │   Test Data  │  │   Jobs       │   │
│  │ - Tech Stack │  │              │  │              │  │              │   │
│  │ - Pages      │  │              │  │              │  │              │   │
│  │ - Summary    │  │              │  │              │  │              │   │
│  │ - Code       │  │              │  │              │  │              │   │
│  │ - Student    │  │              │  │              │  │              │   │
│  │   Info       │  │              │  │              │  │              │   │
│  └──────┬───────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
│         │                                                                   │
│         └─────────────────────────────┬──────────────────────────────────┘ │
│                                       │                                     │
│                              [Validate Inputs]                             │
│                                       │                                     │
└───────────────────────────────────────┼─────────────────────────────────────┘
                                        │
                                        ▼
                        ┌───────────────────────────────┐
                        │   Input Validation Check      │
                        │ (title, summary, tech_stack)  │
                        │ Min 20 words in summary?      │
                        └───────────┬───────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │ (Validation Passed)           │
                    ▼                               │
        ┌──────────────────────────┐       [Show Error]
        │ Store Inputs in Session  │               │
        │ State & Trigger Rerun    │               │
        └──────────┬───────────────┘               │
                   │                               │
                   ▼                               │
        ┌──────────────────────────┐               │
        │ Launch Pipeline in       │               │
        │ Background Thread        │               │
        │ (daemon=True)            │               │
        └──────────┬───────────────┘               │
                   │                               │
                   ▼                               │
                                                   │
     ╔═════════════════════════════════════════════╝
     ║
     ║ (Parallel Process)
     ║
     ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                        LANGRAPH PIPELINE                                     │
│                      (pipeline.py)                                           │
│                                                                              │
│  7-NODE STATE MACHINE (Sequential Execution)                               │
│                                                                              │
│  START                                                                       │
│    │                                                                         │
│    ▼                                                                         │
│  ┌─────────────────────────────┐                                           │
│  │  NODE 1: analyze_input      │                                           │
│  │  ─────────────────────────  │                                           │
│  │  • Validate inputs          │                                           │
│  │  • Log metadata             │                                           │
│  │  • 0 LLM calls             │                                           │
│  │  Progress: 10%              │                                           │
│  └────────────┬────────────────┘                                           │
│               │                                                             │
│               ▼                                                             │
│  ┌─────────────────────────────┐                                           │
│  │  NODE 2: plan_document      │                                           │
│  │  ─────────────────────────  │                                           │
│  │  (planner.py)               │                                           │
│  │  • LLM: Document Planning   │                                           │
│  │  • Output: JSON plan        │                                           │
│  │  • Chapters + pages + words │                                           │
│  │  • Content strategy         │                                           │
│  │  • 1 LLM call              │                                           │
│  │  Progress: 25%              │                                           │
│  └────────────┬────────────────┘                                           │
│               │                                                             │
│               ▼                                                             │
│  ┌─────────────────────────────┐                                           │
│  │ NODE 3: generate_front_matter│                                           │
│  │ ─────────────────────────── │                                           │
│  │ (content_generator.py)      │                                           │
│  │ • Abstract (250-300 words)  │                                           │
│  │ • Acknowledgment (200-250)  │                                           │
│  │ • 2 LLM calls              │                                           │
│  │ Progress: 35%               │                                           │
│  └────────────┬────────────────┘                                           │
│               │                                                             │
│               ▼                                                             │
│  ┌─────────────────────────────┐                                           │
│  │ NODE 4: generate_chapters   │                                           │
│  │ ─────────────────────────── │                                           │
│  │ (content_generator.py)      │                                           │
│  │ • Parallel LLM calls        │                                           │
│  │ • Concurrency: 12           │                                           │
│  │ • 1 call per chapter        │                                           │
│  │ • Typical: 6-10 chapters    │                                           │
│  │ • N LLM calls (parallel)    │                                           │
│  │ Progress: 70%               │                                           │
│  └────────────┬────────────────┘                                           │
│               │                                                             │
│               ▼                                                             │
│  ┌─────────────────────────────┐                                           │
│  │ NODE 5: calibrate_content   │                                           │
│  │ ─────────────────────────── │                                           │
│  │ (content_generator.py)      │                                           │
│  │ • Check word count vs target│                                           │
│  │ • If deviation > 20%:       │                                           │
│  │   - Expand or condense      │                                           │
│  │   - Re-run chapters in batch│                                           │
│  │ • 0-N LLM calls            │                                           │
│  │ Progress: 80%               │                                           │
│  └────────────┬────────────────┘                                           │
│               │                                                             │
│               ▼                                                             │
│  ┌─────────────────────────────┐                                           │
│  │ NODE 6: generate_references │                                           │
│  │ ─────────────────────────── │                                           │
│  │ • IEEE format references    │                                           │
│  │ • 15-25 references          │                                           │
│  │ • 1 LLM call               │                                           │
│  │ Progress: 85%               │                                           │
│  └────────────┬────────────────┘                                           │
│               │                                                             │
│               ▼                                                             │
│  ┌─────────────────────────────┐                                           │
│  │ NODE 7: format_document     │                                           │
│  │ ─────────────────────────── │                                           │
│  │ (doc_formatter.py)          │                                           │
│  │ • Assemble .docx           │                                           │
│  │ • Title page               │                                           │
│  │ • Certificate              │                                           │
│  │ • TOC + LOF + LOT          │                                           │
│  │ • Chapters (parsed MD)     │                                           │
│  │ • References               │                                           │
│  │ • Appendix (code)          │                                           │
│  │ • Page numbers             │                                           │
│  │ • 0 LLM calls             │                                           │
│  │ Progress: 100%              │                                           │
│  └────────────┬────────────────┘                                           │
│               │                                                             │
│               ▼                                                             │
│              END                                                            │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        │ (Return Result)
                                        │
                                        ▼
                    ┌───────────────────────────────┐
                    │   Backend Process Completes   │
                    │   Update st.session_state      │
                    │   signal st.rerun()            │
                    └───────────────────────────────┘
                                        │
                                        ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                    STREAMLIT UI - Results Display                            │
│                                                                              │
│  ┌────────────────────────────────────┐                                     │
│  │ Success Banner (Green)              │                                     │
│  │ Status: Completed                   │                                     │
│  │ Total Tokens: XXXXX                 │                                     │
│  │ Cost: $X.XX (USD)                   │                                     │
│  │ Duration: X min Y sec               │                                     │
│  └────────────────────────────────────┘                                     │
│                                                                              │
│  ┌────────────────────────────────────┐                                     │
│  │ [📥 Download Your Document (.docx)] │                                     │
│  └────────────────────────────────────┘                                     │
│                                                                              │
│  ┌────────────────────────────────────┐                                     │
│  │ 📊 Tracking Details (Expandable)    │                                     │
│  │   - Full JSON tracking data         │                                     │
│  │   - Step-by-step breakdown          │                                     │
│  │   - Colored step cards              │                                     │
│  │   - Token & cost per step           │                                     │
│  └────────────────────────────────────┘                                     │
│                                                                              │
│  ┌────────────────────────────────────┐                                     │
│  │ 🔧 Debug Console (Expandable)       │                                     │
│  │   [   0.0s] 🚀 Pipeline started     │                                     │
│  │   [   0.1s]    Job ID: doc_xxx      │                                     │
│  │   [   0.2s] 🔍 Analyzing input...   │                                     │
│  │   ...                               │                                     │
│  │   [  85.3s] ✅ Generation complete  │                                     │
│  └────────────────────────────────────┘                                     │
│                                                                              │
│  ┌────────────────────────────────────┐                                     │
│  │ [🔄 Generate Another Document]      │                                     │
│  └────────────────────────────────────┘                                     │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Detailed Data Flow Between Modules

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        MODULE INTERACTION FLOW                              │
└─────────────────────────────────────────────────────────────────────────────┘

CONFIG.py (Center Hub)
  ├─ Loaded by: Every module
  ├─ Provides: All constants, env vars, paths
  └─ Key exports:
     • AZURE_OPENAI_* credentials
     • BATCH_CONCURRENCY = 12
     • WORDS_PER_PAGE = 300
     • Font/formatting constants
     • Output/tracking directories


USER INPUT (app.py)
  │
  ├──► VALIDATION (app.py)
  │    • Non-empty title, summary, tech_stack
  │    • Summary >= 20 words
  │
  └──► PIPELINE.py (run_pipeline)
       │
       ├──► NODE 1: analyze_input (pipeline.py)
       │    └──► TRACKER.py
       │         • start_step()
       │         • log_metadata()
       │         • complete_step()
       │
       ├──► NODE 2: plan_document (pipeline.py)
       │    ├──► PLANNER.py (create_document_plan)
       │    │    ├──► LLM_CLIENT.py (call_llm)
       │    │    │    └──► AZURE OPENAI API
       │    │    │         Returns: JSON plan
       │    │    └──► TRACKER.py
       │    │         • log_document_plan()
       │    │         • token counting
       │    │
       │    └──► Output: PipelineState + document_plan
       │
       ├──► NODE 3: generate_front_matter (pipeline.py)
       │    ├──► CONTENT_GENERATOR.py
       │    │    ├──► generate_front_matter() × 2
       │    │    │    ├──► LLM_CLIENT.py (call_llm)
       │    │    │    │    └──► AZURE OPENAI API
       │    │    │    │         Returns: Abstract & Acknowledgment
       │    │    │    └──► TRACKER.py
       │    │    │         • log_step()
       │    │    │         • token counting
       │    │    └──► Output: front_matter list
       │
       ├──► NODE 4: generate_chapters (pipeline.py)
       │    ├──► CONTENT_GENERATOR.py
       │    │    ├──► generate_all_chapters() [async]
       │    │    │    ├──► LLM_CLIENT.py (batch_call_llm)
       │    │    │    │    └──► AZURE OPENAI API (12 parallel calls)
       │    │    │    │         Returns: All chapters content
       │    │    │    └──► TRACKER.py
       │    │    │         • log_parallel_batch()
       │    │    │         • cumulative token count
       │    │    └──► Output: chapters_content list
       │
       ├──► NODE 5: calibrate_content (pipeline.py)
       │    ├──► CONTENT_GENERATOR.py
       │    │    ├──► calibrate_content() [async]
       │    │    │    ├─ Check: |actual_words - target_words| / target
       │    │    │    ├─ If deviation > 20%:
       │    │    │    │  ├──► LLM_CLIENT.py (batch_call_llm)
       │    │    │    │  │    └──► AZURE OPENAI API (re-generate)
       │    │    │    │  └──► TRACKER.py
       │    │    │    │       • log_calibration()
       │    │    │    └─ Else: Skip this chapter
       │    │    └──► Output: calibrated_chapters
       │
       ├──► NODE 6: generate_references (pipeline.py)
       │    ├──► CONTENT_GENERATOR.py
       │    │    ├──► (Call LLM to generate IEEE refs)
       │    │    │    ├──► LLM_CLIENT.py (call_llm)
       │    │    │    │    └──► AZURE OPENAI API
       │    │    │    │         Returns: 15-25 IEEE references
       │    │    │    └──► TRACKER.py
       │    │    │         • log_step()
       │    │    │         • token counting
       │    │    └──► Output: references_content
       │
       └──► NODE 7: format_document (pipeline.py)
            ├──► DOC_FORMATTER.py
            │    ├──► DocumentFormatter.__init__()
            │    │    • Create new Document()
            │    │    • Setup A4 page layout
            │    │    • Setup styles (Normal, Heading 1/2/3, Code)
            │    │
            │    ├──► add_title_page()
            │    ├──► add_certificate_page()
            │    ├──► add_acknowledgment()
            │    ├──► add_abstract()
            │    ├──► add_table_of_contents()
            │    ├──► add_list_of_figures()
            │    ├──► add_list_of_tables()
            │    │
            │    ├──► add_chapter() × N
            │    │    └──► _parse_and_add_content()
            │    │         • Parse markdown
            │    │         • Handle ## Heading 2
            │    │         • Handle ### Heading 3
            │    │         • Handle ```code``` blocks
            │    │         • Handle [DIAGRAM: type]
            │    │         • Handle markdown tables
            │    │         • Handle **bold**, *italic*
            │    │
            │    ├──► add_references()
            │    ├──► add_appendix()
            │    ├──► add_page_numbers()
            │    │
            │    └──► save()
            │         • Write to: output/doc_YYYYMMDD_HHMMSS.docx
            │         • Return: absolute path
            │
            ├──► TRACKER.py
            │    • complete_job()
            │    • save final JSON
            │
            └──► Output: .docx file + tracking JSON


TRACKING.py (Cross-cutting Concern)
  │
  ├─ Initialized: Each pipeline run (job_id)
  ├─ Used by: All 7 pipeline nodes
  ├─ Persists to: tracking/doc_YYYYMMDD_HHMMSS.json
  │
  └─ Tracks:
     • Job ID, status, timestamps
     • Each node's step_id, duration, tokens, cost
     • Cumulative token counts
     • Estimated USD cost
     • Error messages (if any)


LLM_CLIENT.py (LLM Interface)
  │
  ├─ Functions:
  │  ├──► get_llm() → AzureChatOpenAI instance
  │  ├──► count_tokens(text) → int
  │  ├──► call_llm() → {content, input_tokens, output_tokens}
  │  ├──► call_llm_async() → same (async version)
  │  └──► batch_call_llm(calls[], concurrency=12)
  │       └─ Uses asyncio.Semaphore to gate parallel calls
  │       └─ Returns list of responses
  │
  └─ All calls made to: AZURE OPENAI API
```

---

## 3. Async & Threading Model

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    STREAMLIT EVENT LOOP                                  │
│                                                                          │
│  Main Thread (Streamlit's event loop)                                  │
│    │                                                                     │
│    ├─► Render UI (form inputs, sidebar, etc.)                          │
│    │                                                                     │
│    ├─► On "Generate" button click:                                     │
│    │   └─► Spawn: threading.Thread(target=_run_pipeline, daemon=True) │
│    │       • Pass inputs dict                                           │
│    │       • Main thread continues                                      │
│    │       • Set st.session_state.generation_started = True            │
│    │       • Call st.rerun() → triggers second page render             │
│    │                                                                     │
│    └─► Second render:                                                   │
│        ├─► Show progress bar placeholder                               │
│        ├─► Show debug console placeholder (st.code)                    │
│        │                                                                 │
│        └─► polling_loop (every 1 second):                              │
│            └─► Call tracker.get_logs()                                 │
│                └─► Call tracker.get_progress()                         │
│                    └─► Update UI elements (progress bar, console)      │
│                                                                          │
│                                                                          │
│  Background Thread (_run_pipeline)                                      │
│    │                                                                     │
│    ├─► run_pipeline() synchronously                                    │
│    │   (Internally uses nest_asyncio.apply() to allow async)          │
│    │                                                                     │
│    ├─► LangGraph compiles and invokes pipeline                        │
│    │   • Node 1-7 execute sequentially                                 │
│    │   • Each node can call async functions                            │
│    │   • batch_call_llm uses asyncio.gather() with Semaphore        │
│    │   • Async calls batched (12 parallel)                            │
│    │                                                                     │
│    └─► On completion:                                                   │
│        ├─► Set st.session_state.result = result                        │
│        └─► Call st.rerun() → triggers third page render               │
│            (shows results, download button, etc.)                       │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 4. LLM Call Breakdown (Token Flow)

```
┌────────────────────────────────────────────────────────────────────┐
│               LLM CALLS BY PIPELINE NODE                          │
└────────────────────────────────────────────────────────────────────┘

NODE 2: plan_document
  └─ 1 LLM call
     System Prompt: PLANNER_SYSTEM_PROMPT (detailed rules)
     User Prompt: {title, summary, code, tech_stack, target_pages, ...}
     Output Tokens: ~3000-5000
     Input Tokens: ~5000-10000 (includes full project info)

     Response: JSON document plan with:
     {
       "chapters": [
         {
           "chapter_number": 1,
           "title": "Introduction",
           "page_allocation": 10,
           "word_target": 3000,
           "sections": [...]
         },
         ...
       ],
       "content_strategy": "elaborate|summarize|balanced",
       "total_pages": 60
     }


NODE 3: generate_front_matter
  ├─ 1 LLM call (Abstract)
  │  System: FRONT_MATTER_SYSTEM_PROMPT
  │  User: {project_title, project_summary, ...}
  │  Output: Abstract (250-300 words) ≈ 400-500 tokens
  │
  └─ 1 LLM call (Acknowledgment)
     System: FRONT_MATTER_SYSTEM_PROMPT
     User: {project_title, student_name, ...}
     Output: Acknowledgment (200-250 words) ≈ 300-400 tokens


NODE 4: generate_chapters (PARALLEL)
  └─ N LLM calls (one per chapter, e.g., 8 chapters = 8 calls)
     │
     Concurrent Calls (Semaphore = 12)
     │
     Each call:
       System: CHAPTER_SYSTEM_PROMPT
       User: {chapter title, sections, word_target, project_code, ...}
       Output Tokens: chapter_word_target / 0.75 ≈ 4000 tokens per chapter

     For 60-page doc with 8 chapters:
       Total Output: ≈ 32,000 tokens
       Total Input: ≈ 40,000 tokens (includes code samples)

     Timeline:
       - Sequential: ~3-5 min (one chapter at a time)
       - Parallel (12 concurrent): ~15-30 sec


NODE 5: calibrate_content (CONDITIONAL PARALLEL)
  └─ 0 to N LLM calls (only if chapter deviation > 20%)

     For each out-of-target chapter:
       System: CHAPTER_SYSTEM_PROMPT (with expand/condense instructions)
       User: {same chapter} + "expand this by X words" or "condense..."
       Output: Re-generated chapter content

     Cost:
       - 20% of 60 pages ≈ ~3-5 chapters re-generated
       - ≈ 12,000-20,000 additional tokens

     Timing: Parallel batch of re-generations (Semaphore = 12)


NODE 6: generate_references
  └─ 1 LLM call
     System: (generic prompt for IEEE references)
     User: {tech_stack, project_summary}
     Output: 15-25 IEEE-format references ≈ 1000-1500 tokens


TOTAL TOKEN SUMMARY (60-page example)
  ├─ Node 2 (Planning): 8K input + 4K output = 12K
  ├─ Node 3 (Front Matter): 8K input + 1K output = 9K
  ├─ Node 4 (Chapters): 40K input + 32K output = 72K
  ├─ Node 5 (Calibration): 15K input + 15K output = 30K (estimated)
  └─ Node 6 (References): 2K input + 1.5K output = 3.5K

  TOTAL: ~127K tokens
  Cost (GPT-4o pricing): ~$0.40-0.60 USD
```

---

## 5. Document Generation Output Structure

```
┌────────────────────────────────────────────────────────────────────────┐
│                    GENERATED .DOCX STRUCTURE                          │
└────────────────────────────────────────────────────────────────────────┘

output/doc_20260212_232509.docx
  │
  ├─ [PAGE 1] Title Page
  │  ├─ College Name (18pt bold, uppercase, centered)
  │  ├─ Department (12pt, centered)
  │  ├─ "A Project Report On"
  │  ├─ Project Title (18pt bold, blue, centered)
  │  ├─ Student Name, Roll Number
  │  ├─ Guide Name
  │  └─ Academic Year
  │
  ├─ [PAGE 2] Certificate
  │  ├─ Formal certification text
  │  └─ Signature table (3 columns)
  │     ├─ Project Guide
  │     ├─ Head of Department
  │     └─ External Examiner
  │
  ├─ [PAGE 3] Acknowledgment
  │  └─ LLM-generated acknowledgment (200-250 words)
  │
  ├─ [PAGE 4-5] Abstract
  │  └─ LLM-generated abstract (250-300 words)
  │
  ├─ [PAGE 6-7] Table of Contents
  │  └─ Word field code (TOC \o "1-3" \h \z \u)
  │     User right-clicks → "Update Field" to populate
  │
  ├─ [PAGE 8] List of Figures
  │  └─ Placeholder (user updates manually)
  │
  ├─ [PAGE 9] List of Tables
  │  └─ Placeholder (user updates manually)
  │
  ├─ [PAGE 10-70] Chapters (Example: 60-page doc)
  │  │
  │  ├─ Chapter 1: Introduction (8 pages, 2400 words)
  │  │  ├─ Heading 1: "Chapter 1: Introduction"
  │  │  ├─ Heading 2: "1.1 Background"
  │  │  │  └─ Body text (Times New Roman 12pt, 1.5 line spacing)
  │  │  ├─ Heading 2: "1.2 Problem Statement"
  │  │  │  └─ Body text
  │  │  ├─ Heading 2: "1.3 Objectives"
  │  │  │  └─ Bulleted list
  │  │  ├─ Code block (if present)
  │  │  │  └─ Consolas 10pt, gray background, bordered table
  │  │  ├─ [DIAGRAM: System Architecture - description]
  │  │  │  └─ Bordered box, gray placeholder, auto-captioned "Figure 1.1: ..."
  │  │  └─ Markdown table (if present)
  │  │     └─ Blue header row (#D9E2F3), borders
  │  │
  │  ├─ Chapter 2: Literature Review (7 pages, 2100 words)
  │  ├─ Chapter 3: System Requirements & Analysis (6 pages, 1800 words)
  │  ├─ Chapter 4: System Design (10 pages, 3000 words)
  │  │  └─ [DIAGRAM: ER Diagram]
  │  │  └─ [DIAGRAM: Data Flow Diagram]
  │  │  └─ [DIAGRAM: Use Case Diagram]
  │  ├─ Chapter 5: Implementation (12 pages, 3600 words)
  │  │  └─ Code blocks
  │  ├─ Chapter 6: Testing (8 pages, 2400 words)
  │  │  └─ Test case tables
  │  ├─ Chapter 7: Results & Discussion (5 pages, 1500 words)
  │  │  └─ Screenshots (as [DIAGRAM: Screenshot])
  │  └─ Chapter 8: Conclusion & Future Scope (4 pages, 1200 words)
  │
  ├─ [PAGE 71-73] References
  │  └─ 15-25 IEEE-format references
  │     Example:
  │     [1] J. Doe, "Machine Learning in Python," IEEE Transactions, 2023.
  │     [2] A. Smith, "Cloud Computing Fundamentals," Journal of Computing, 2022.
  │
  └─ [PAGE 74-80+] Appendix
     └─ Source Code (first 10,000 characters)
        └─ Code blocks with syntax highlighting


Page Numbers:
  └─ Inserted in footer of every page (Word PAGE field code)


Section Format:
  Margins:    1.25" left, 1.0" top/bottom/right
  Font:       Times New Roman 12pt, body text
  Headings:   Heading 1 (16pt), Heading 2 (14pt), Heading 3 (12pt)
  Spacing:    1.5× line spacing throughout
  Page Size:  A4 (8.27" × 11.69")
```

---

## 6. Tracking File (JSON) Structure

```
tracking/doc_20260212_232509.json
│
├─ "job_id": "doc_20260212_232509"
├─ "status": "completed" (or "failed")
├─ "started_at": "2026-02-12T23:25:09"
├─ "completed_at": "2026-02-12T23:28:15"
│
├─ "user_inputs": {
│    "project_title": "Smart Attendance System using Face Recognition",
│    "project_summary": "...",
│    "tech_stack": "Python, OpenCV, Flask, SQLite",
│    "target_pages": 60,
│    "student_name": "John Doe",
│    "college_name": "XYZ University",
│    ...
│  }
│
├─ "document_plan": {
│    "chapters": [
│      {
│        "chapter_number": 1,
│        "title": "Introduction",
│        "page_allocation": 8,
│        "word_target": 2400,
│        "sections": [...]
│      },
│      ...
│    ],
│    "content_strategy": "balanced",
│    "total_pages": 60
│  }
│
├─ "total_tokens": {
│    "input": 127000,
│    "output": 85000,
│    "total": 212000
│  }
│
├─ "cost_estimate_usd": 0.4325
├─ "total_duration_seconds": 186.42
│
└─ "steps": [
     {
       "step_id": "step_1",
       "step_name": "input_analysis",
       "description": "Validating inputs...",
       "status": "completed",
       "started_at": "2026-02-12T23:25:09",
       "completed_at": "2026-02-12T23:25:10",
       "duration_seconds": 0.01,
       "tokens": {
         "input": 0,
         "output": 0,
         "total": 0
       },
       "llm_calls": 0
     },
     {
       "step_id": "step_2",
       "step_name": "plan_document",
       "description": "Planning document structure...",
       "status": "completed",
       "started_at": "2026-02-12T23:25:10",
       "completed_at": "2026-02-12T23:25:15",
       "duration_seconds": 5.2,
       "tokens": {
         "input": 10000,
         "output": 4000,
         "total": 14000
       },
       "llm_calls": 1
     },
     ...
   ]
```

---

## 7. Error Handling & Fallback Mechanisms

```
┌───────────────────────────────────────────────────────────────────────┐
│              ERROR HANDLING FLOW                                      │
└───────────────────────────────────────────────────────────────────────┘

INPUT VALIDATION (app.py)
  ├─ If title is empty → Show error, don't proceed
  ├─ If summary < 20 words → Show error, don't proceed
  └─ If tech_stack is empty → Show error, don't proceed

PIPELINE EXECUTION
  │
  ├─► Node succeeds → Update status, log, continue
  │
  └─► Node fails:
      ├─ Catch exception
      ├─ Log error to tracker
      ├─ Set status = "failed"
      ├─ Return error message
      ├─ Halt pipeline (no further nodes execute)
      │
      └─► Display error in UI:
          ├─ Red banner: "Generation Failed"
          ├─ Error message
          ├─ Suggest troubleshooting steps
          └─ [🔄 Try Again] button

LLM API ERRORS (batch_call_llm)
  │
  └─► Per-call error handling:
      ├─ Catch exception for each call
      ├─ Return: {content: "ERROR: ...", error: "..."}
      ├─ Don't abort entire batch
      ├─ Log error to tracker
      │
      └─► During calibration:
          ├─ If chapter re-gen fails
          ├─ Keep original chapter content
          ├─ Log warning
          └─ Continue with next chapter

ASYNC ISSUES (pipeline.py)
  │
  ├─ Problem: "RuntimeError: This event loop is already running"
  │  ├─ Cause: Streamlit already has asyncio event loop
  │  ├─ Solution: nest_asyncio.apply() at top of pipeline.py
  │  └─ Fallback: ThreadPoolExecutor-based patch (if nest_asyncio unavailable)
  │
  └─ Semaphore gating:
     └─ Limits parallel calls to 12
     └─ Prevents rate limiting on Azure OpenAI

DOCUMENT FORMATTING ERRORS
  └─ If markdown parsing fails:
     ├─ Log warning in tracker
     ├─ Render text as plain paragraph
     ├─ Continue document assembly
     └─ Document still generates (may lose some formatting)
```

---

## 8. Performance & Optimization

```
┌───────────────────────────────────────────────────────────────────────┐
│            PERFORMANCE METRICS BY DOCUMENT SIZE                       │
└───────────────────────────────────────────────────────────────────────┘

30-PAGE DOCUMENT
  Chapters: 5-6
  Total tokens: ~50K
  Estimated cost: $0.15-0.30
  Duration (sequential): 3-5 min
  Duration (parallel 12): 1-2 min
  ├─ Planning: 3-5 sec
  ├─ Front matter: 5-8 sec
  ├─ Chapters (parallel): 15-25 sec (6 parallel calls)
  ├─ Calibration: 5-10 sec
  ├─ References: 3-5 sec
  └─ Formatting: 2-3 sec

60-PAGE DOCUMENT (Most Common)
  Chapters: 8
  Total tokens: ~120K
  Estimated cost: $0.30-0.50
  Duration (sequential): 6-10 min
  Duration (parallel 12): 2-4 min
  ├─ Planning: 5-8 sec
  ├─ Front matter: 5-8 sec
  ├─ Chapters (parallel): 30-45 sec (8 parallel calls)
  ├─ Calibration: 10-20 sec
  ├─ References: 3-5 sec
  └─ Formatting: 2-3 sec

120-PAGE DOCUMENT
  Chapters: 12
  Total tokens: ~250K
  Estimated cost: $0.60-1.00
  Duration (sequential): 12-20 min
  Duration (parallel 12): 5-8 min
  ├─ Planning: 5-8 sec
  ├─ Front matter: 5-8 sec
  ├─ Chapters (parallel): 60-90 sec (12 parallel calls)
  ├─ Calibration: 20-40 sec
  ├─ References: 3-5 sec
  └─ Formatting: 3-5 sec

250-PAGE DOCUMENT
  Chapters: 20
  Total tokens: ~500K
  Estimated cost: $1.50-2.50
  Duration (sequential): 25-40 min
  Duration (parallel 12): 10-15 min
  ├─ Planning: 5-8 sec
  ├─ Front matter: 5-8 sec
  ├─ Chapters (parallel, 2 batches): 120-180 sec
  │                                  (12 + remaining 8)
  ├─ Calibration: 30-60 sec
  ├─ References: 3-5 sec
  └─ Formatting: 5-8 sec

OPTIMIZATION LEVERS
  ├─ Increase BATCH_CONCURRENCY (12 → 20) → faster, higher rate limit risk
  ├─ Decrease target_pages → fewer chapters, faster generation
  ├─ More detailed summary → LLM generates better content (first pass)
  │                        → fewer re-calibrations
  └─ Simpler college format → reduces LLM thinking time

BOTTLENECKS
  ├─ Planning: Small LLM call, typically fast
  ├─ Chapters: Largest bottleneck (70% of time)
  │   └─ Mitigation: Parallel batch calls
  └─ Calibration: Unpredictable (depends on content quality)
     └─ Mitigation: Better project summary input
```

---

## Summary

This **Project Documentation Generator** is a sophisticated **AI-powered document automation system** that:

1. **Takes user input** (project info, summary, code, student details)
2. **Plans document structure** (chapters, pages, word targets) via LLM
3. **Generates content** (8+ chapters) in parallel (12 concurrent LLM calls)
4. **Auto-calibrates** chapters that deviate >20% from word targets
5. **Assembles a professional .docx** (title, certificate, TOC, chapters, references, appendix)
6. **Tracks everything** (tokens, timing, costs, progress logs)

**Key Technologies**: Streamlit (UI) → LangGraph (pipeline) → LangChain + Azure OpenAI (LLM) → python-docx (document)

**Performance**: 60-page document in 2-4 minutes, ~$0.40 cost.

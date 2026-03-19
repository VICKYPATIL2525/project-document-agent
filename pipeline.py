"""
LangGraph Pipeline - Orchestrates the entire document generation process.
Defines the state machine: Input → Plan → Generate → Calibrate → Format → Output
"""
import asyncio
import json

# Patch asyncio to allow nested event loops (needed when running inside Streamlit)
try:
    import nest_asyncio
    nest_asyncio.apply()
except ImportError:
    # Fallback: patch asyncio.run to work inside an already-running loop
    _original_asyncio_run = asyncio.run

    def _patched_asyncio_run(coro, **kwargs):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        if loop and loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                return pool.submit(asyncio.run, coro).result()
        return _original_asyncio_run(coro, **kwargs)

    asyncio.run = _patched_asyncio_run
from datetime import datetime
from typing import TypedDict, Annotated, Optional
from langgraph.graph import StateGraph, START, END
from tracker import ProcessTracker
from planner import create_document_plan
from content_generator import (
    generate_all_chapters,
    generate_front_matter,
    calibrate_content,
)
from doc_formatter import DocumentFormatter
from config import OUTPUT_DIR, PLANNER_MODEL, GENERATOR_MODEL


# ─── State Definition ─────────────────────────────────────────────────────────

class PipelineState(TypedDict):
    """State that flows through the pipeline."""
    # User Inputs
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

    # Pipeline Data
    job_id: str
    document_plan: Optional[dict]
    chapters_content: Optional[list]
    front_matter: Optional[list]
    references_content: Optional[str]
    output_file: Optional[str]

    # Status
    status: str
    error: Optional[str]
    progress_pct: int


# ─── Global tracker registry ──────────────────────────────────────────────────
_trackers: dict[str, ProcessTracker] = {}


def get_tracker(job_id: str) -> ProcessTracker:
    """Get or create a tracker for the given job ID."""
    if job_id not in _trackers:
        _trackers[job_id] = ProcessTracker(job_id)
    return _trackers[job_id]


# ─── Node Functions ───────────────────────────────────────────────────────────

def analyze_input_node(state: PipelineState) -> dict:
    """Analyze and validate user inputs."""
    tracker = get_tracker(state["job_id"])
    tracker.log("🔍 Starting input analysis...")
    step_id = tracker.start_step("input_analysis", "Analyzing and validating user inputs")

    # Store user inputs in tracker
    tracker.set_user_inputs({
        "project_title": state["project_title"],
        "target_pages": state["target_pages"],
        "summary_word_count": len(state["project_summary"].split()),
        "code_provided": bool(state["project_code"]),
        "code_length": len(state["project_code"]) if state["project_code"] else 0,
        "college_format": bool(state["college_format"]),
    })

    tracker.log(f"   Project: {state['project_title']}")
    tracker.log(f"   Target pages: {state['target_pages']}")
    tracker.log(f"   Summary: {len(state['project_summary'].split())} words")
    tracker.log(f"   Code provided: {'Yes' if state['project_code'] else 'No'}")
    tracker.complete_step(step_id, input_tokens=0, output_tokens=0, llm_calls=0)
    tracker.log("✅ Input analysis complete")

    return {
        "status": "input_analyzed",
        "progress_pct": 10,
    }


def plan_document_node(state: PipelineState) -> dict:
    """Create the document structure plan using LLM."""
    tracker = get_tracker(state["job_id"])
    tracker.log(f"📝 Planning document structure (model: {PLANNER_MODEL})...")

    plan = create_document_plan(
        project_title=state["project_title"],
        project_summary=state["project_summary"],
        project_code=state["project_code"],
        tech_stack=state["tech_stack"],
        target_pages=state["target_pages"],
        college_format=state["college_format"],
        additional_info=state["additional_info"],
        tracker=tracker,
    )

    num_chapters = len(plan.get("chapters", []))
    tracker.log(f"✅ Document plan created: {num_chapters} chapters")
    for ch in plan.get("chapters", []):
        tracker.log(f"   Ch {ch['chapter_number']}: {ch['title']} ({ch['page_allocation']} pages, {ch['word_target']} words)")

    return {
        "document_plan": plan,
        "status": "document_planned",
        "progress_pct": 25,
    }


def generate_front_matter_node(state: PipelineState) -> dict:
    """Generate front matter content (abstract, acknowledgment)."""
    tracker = get_tracker(state["job_id"])
    tracker.log("📄 Generating front matter...")

    front_matter = []

    # Generate abstract
    tracker.log("   Generating abstract...")
    abstract = generate_front_matter(
        section_type="abstract",
        project_title=state["project_title"],
        project_summary=state["project_summary"],
        student_name=state["student_name"],
        college_name=state["college_name"],
        guide_name=state["guide_name"],
        department=state["department"],
        year=state["year"],
        tracker=tracker,
    )
    front_matter.append(abstract)
    tracker.log("   ✅ Abstract done")

    # Generate acknowledgment
    tracker.log("   Generating acknowledgment...")
    acknowledgment = generate_front_matter(
        section_type="acknowledgment",
        project_title=state["project_title"],
        project_summary=state["project_summary"],
        student_name=state["student_name"],
        college_name=state["college_name"],
        guide_name=state["guide_name"],
        department=state["department"],
        year=state["year"],
        tracker=tracker,
    )
    front_matter.append(acknowledgment)
    tracker.log("✅ Front matter complete")

    return {
        "front_matter": front_matter,
        "status": "front_matter_generated",
        "progress_pct": 35,
    }


def generate_chapters_node(state: PipelineState) -> dict:
    """Generate all chapter content in parallel batches."""
    tracker = get_tracker(state["job_id"])
    num_chapters = len(state["document_plan"].get("chapters", []))
    tracker.log(f"📚 Generating {num_chapters} chapters in parallel batches (model: {GENERATOR_MODEL})...")

    # Run async content generation
    chapters = asyncio.run(
        generate_all_chapters(
            plan=state["document_plan"],
            project_summary=state["project_summary"],
            project_code=state["project_code"],
            tech_stack=state["tech_stack"],
            additional_info=state["additional_info"],
            tracker=tracker,
        )
    )

    for ch in chapters:
        tracker.log(f"   ✅ Ch {ch['chapter_number']}: {ch['title']} — {ch['word_count']} words")
    tracker.log(f"✅ All {len(chapters)} chapters generated")

    return {
        "chapters_content": chapters,
        "status": "chapters_generated",
        "progress_pct": 70,
    }


def calibrate_content_node(state: PipelineState) -> dict:
    """Check content against page targets and adjust if needed."""
    tracker = get_tracker(state["job_id"])
    tracker.log("⚖️  Calibrating content against page targets...")

    calibrated = asyncio.run(
        calibrate_content(
            chapters=state["chapters_content"],
            plan=state["document_plan"],
            tracker=tracker,
        )
    )

    tracker.log("✅ Content calibration complete")

    return {
        "chapters_content": calibrated,
        "status": "content_calibrated",
        "progress_pct": 80,
    }


def generate_references_node(state: PipelineState) -> dict:
    """Generate references/bibliography section."""
    tracker = get_tracker(state["job_id"])
    tracker.log(f"📚 Generating IEEE references (model: {PLANNER_MODEL})...")
    step_id = tracker.start_step("generate_references", "Generating references section")

    from llm_client import call_llm

    result = call_llm(
        system_prompt="""Generate a list of 15-25 academic references for a final year project report.
Use IEEE format. Include a mix of:
- Research papers from relevant conferences/journals
- Books on the subject
- Official documentation links
- Relevant web resources
Make them realistic and relevant to the project's technology stack.
Return only the numbered reference list, no other text.""",
        user_prompt=f"""Project: {state['project_title']}
Technology Stack: {state['tech_stack']}
Summary: {state['project_summary'][:1000]}""",
        temperature=0.5,
        max_tokens=2048,
        model=PLANNER_MODEL,
    )

    tracker.complete_step(
        step_id,
        input_tokens=result["input_tokens"],
        output_tokens=result["output_tokens"],
    )
    tracker.log("✅ References generated")

    return {
        "references_content": result["content"],
        "status": "references_generated",
        "progress_pct": 85,
    }


def format_document_node(state: PipelineState) -> dict:
    """Assemble everything into a formatted Word document."""
    tracker = get_tracker(state["job_id"])
    tracker.log("📄 Assembling Word document...")
    step_id = tracker.start_step("document_formatting", "Assembling and formatting Word document")

    try:
        filename = f"{state['job_id']}.docx"
        doc = DocumentFormatter(filename)

        # 1. Title Page
        tracker.log("   Adding title page...")
        doc.add_title_page(
            project_title=state["project_title"],
            student_name=state["student_name"],
            roll_number=state["roll_number"],
            college_name=state["college_name"],
            department=state["department"],
            guide_name=state["guide_name"],
            year=state["year"],
        )

        # 2. Certificate Page
        tracker.log("   Adding certificate page...")
        doc.add_certificate_page(
            project_title=state["project_title"],
            student_name=state["student_name"],
            roll_number=state["roll_number"],
            college_name=state["college_name"],
            department=state["department"],
            guide_name=state["guide_name"],
        )

        # 3. Acknowledgment
        ack_content = ""
        abstract_content = ""
        for fm in (state.get("front_matter") or []):
            if fm["type"] == "acknowledgment":
                ack_content = fm["content"]
            elif fm["type"] == "abstract":
                abstract_content = fm["content"]

        doc.add_acknowledgment(ack_content)

        # 4. Abstract
        doc.add_abstract(abstract_content)

        # 5. Table of Contents
        doc.add_table_of_contents()

        # 6. List of Figures
        doc.add_list_of_figures()

        # 7. List of Tables
        doc.add_list_of_tables()

        # 8. Chapters
        for chapter in (state.get("chapters_content") or []):
            tracker.log(f"   Formatting Ch {chapter['chapter_number']}: {chapter['title']}")
            doc.add_chapter(
                chapter_number=chapter["chapter_number"],
                title=chapter["title"],
                content=chapter["content"],
            )

        # 9. References
        doc.add_references(state.get("references_content", ""))

        # 10. Appendix
        appendix_code = state.get("project_code", "")
        if appendix_code:
            doc.add_appendix(f"## Source Code\n\n```\n{appendix_code[:10000]}\n```")
        else:
            doc.add_appendix()

        # Save
        tracker.log("   Saving .docx file...")
        output_path = doc.save()

        tracker.complete_step(step_id, input_tokens=0, output_tokens=0, llm_calls=0)
        tracker.log(f"✅ Document saved: {output_path}")
        tracker.complete_job(output_file=output_path)

        return {
            "output_file": output_path,
            "status": "completed",
            "progress_pct": 100,
        }

    except Exception as e:
        tracker.fail_step(step_id, str(e))
        tracker.fail_job(str(e))
        return {
            "status": "failed",
            "error": str(e),
        }


# ─── Build the Graph ──────────────────────────────────────────────────────────

def build_pipeline() -> StateGraph:
    """Build and compile the document generation pipeline."""
    graph = StateGraph(PipelineState)

    # Add nodes
    graph.add_node("analyze_input", analyze_input_node)
    graph.add_node("plan_document", plan_document_node)
    graph.add_node("generate_front_matter", generate_front_matter_node)
    graph.add_node("generate_chapters", generate_chapters_node)
    graph.add_node("calibrate_content", calibrate_content_node)
    graph.add_node("generate_references", generate_references_node)
    graph.add_node("format_document", format_document_node)

    # Define edges (linear pipeline)
    graph.add_edge(START, "analyze_input")
    graph.add_edge("analyze_input", "plan_document")
    graph.add_edge("plan_document", "generate_front_matter")
    graph.add_edge("generate_front_matter", "generate_chapters")
    graph.add_edge("generate_chapters", "calibrate_content")
    graph.add_edge("calibrate_content", "generate_references")
    graph.add_edge("generate_references", "format_document")
    graph.add_edge("format_document", END)

    return graph.compile()


# ─── Main Entry Point ─────────────────────────────────────────────────────────

def run_pipeline(
    project_title: str,
    project_summary: str,
    project_code: str = "",
    tech_stack: str = "",
    target_pages: int = 50,
    college_format: str = "",
    additional_info: str = "",
    student_name: str = "Student Name",
    roll_number: str = "000",
    college_name: str = "University",
    department: str = "Department of Computer Science",
    guide_name: str = "Prof. Guide",
    year: str = "2025-2026",
) -> dict:
    """
    Run the complete document generation pipeline.

    Returns:
        dict with: job_id, output_file, status, tracking_file
    """
    # Generate job ID
    job_id = f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Initialize tracker
    tracker = ProcessTracker(job_id)
    _trackers[job_id] = tracker
    tracker.set_status("running")
    tracker.log("🚀 Pipeline started")
    tracker.log(f"   Job ID: {job_id}")

    # Build and run pipeline
    pipeline = build_pipeline()

    initial_state = {
        "project_title": project_title,
        "project_summary": project_summary,
        "project_code": project_code,
        "tech_stack": tech_stack,
        "target_pages": target_pages,
        "college_format": college_format,
        "additional_info": additional_info,
        "student_name": student_name,
        "roll_number": roll_number,
        "college_name": college_name,
        "department": department,
        "guide_name": guide_name,
        "year": year,
        "job_id": job_id,
        "document_plan": None,
        "chapters_content": None,
        "front_matter": None,
        "references_content": None,
        "output_file": None,
        "status": "started",
        "error": None,
        "progress_pct": 0,
    }

    try:
        result = pipeline.invoke(initial_state)
        tracker.log("🎉 Pipeline finished successfully!")
        return {
            "job_id": job_id,
            "status": result.get("status", "completed"),
            "output_file": result.get("output_file", ""),
            "tracking_file": tracker.file_path,
            "total_tokens": tracker.data["total_tokens"],
            "cost_usd": tracker.data["cost_estimate_usd"],
            "duration_seconds": tracker.data["total_duration_seconds"],
            "logs": tracker.get_logs(),
        }
    except Exception as e:
        tracker.log(f"❌ Pipeline failed: {str(e)}")
        tracker.fail_job(str(e))
        return {
            "job_id": job_id,
            "status": "failed",
            "error": str(e),
            "tracking_file": tracker.file_path,
            "logs": tracker.get_logs(),
        }

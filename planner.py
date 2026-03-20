"""
Document Planner - Analyzes user inputs and creates a structured document plan.
Uses LLM to generate chapter outlines with page allocations.
"""
import json
from config import WORDS_PER_PAGE, calculate_max_tokens, PLANNER_MODEL
from llm_client import call_llm
from tracker import ProcessTracker


def _get_front_matter_plan(target_pages: int) -> list[dict]:
    """Return front matter list scaled to target page count."""
    if target_pages <= 15:
        # Minimal front matter for small documents
        return [
            {"type": "title_page", "page_allocation": 1},
            {"type": "certificate", "page_allocation": 1},
            {"type": "acknowledgment", "page_allocation": 1},
            {"type": "abstract", "page_allocation": 1},
            {"type": "table_of_contents", "page_allocation": 1},
        ]
    elif target_pages <= 30:
        return [
            {"type": "title_page", "page_allocation": 1},
            {"type": "certificate", "page_allocation": 1},
            {"type": "acknowledgment", "page_allocation": 1},
            {"type": "abstract", "page_allocation": 1},
            {"type": "table_of_contents", "page_allocation": 1},
            {"type": "list_of_figures", "page_allocation": 1},
            {"type": "list_of_tables", "page_allocation": 1},
        ]
    else:
        return [
            {"type": "title_page", "page_allocation": 1},
            {"type": "certificate", "page_allocation": 1},
            {"type": "acknowledgment", "page_allocation": 1},
            {"type": "abstract", "page_allocation": 2},
            {"type": "table_of_contents", "page_allocation": 2},
            {"type": "list_of_figures", "page_allocation": 1},
            {"type": "list_of_tables", "page_allocation": 1},
        ]


def _get_back_matter_plan(target_pages: int) -> list[dict]:
    """Return back matter list scaled to target page count."""
    if target_pages <= 15:
        return [
            {"type": "references", "page_allocation": 1},
        ]
    elif target_pages <= 30:
        return [
            {"type": "references", "page_allocation": 2},
            {"type": "appendix", "page_allocation": 2},
        ]
    else:
        return [
            {"type": "references", "page_allocation": 3},
            {"type": "appendix", "page_allocation": max(3, int(target_pages * 0.04))},
        ]


def _get_max_chapters(target_pages: int) -> int:
    """Return max number of chapters based on target page count."""
    if target_pages <= 12:
        return 4
    elif target_pages <= 20:
        return 5
    elif target_pages <= 40:
        return 6
    elif target_pages <= 80:
        return 8
    else:
        return 10


def _build_system_prompt(target_pages: int) -> str:
    """Build the planner system prompt dynamically based on target pages."""
    front_matter = _get_front_matter_plan(target_pages)
    back_matter = _get_back_matter_plan(target_pages)
    max_chapters = _get_max_chapters(target_pages)
    front_matter_json = json.dumps(front_matter, indent=4)
    back_matter_json = json.dumps(back_matter, indent=4)

    # Choose chapter guidance based on size
    if target_pages <= 15:
        chapter_guidance = (
            "For this SMALL document, use only 3-4 short chapters. "
            "Combine related topics (e.g., 'Introduction & Literature Review', 'Design & Implementation'). "
            "Keep each chapter to 1-2 pages. Do NOT use all 8 standard chapters — merge them."
        )
    elif target_pages <= 30:
        chapter_guidance = (
            "For this MEDIUM document, use 4-5 chapters. "
            "You may merge some standard chapters (e.g., combine Testing with Results)."
        )
    else:
        chapter_guidance = (
            "Standard chapters: Introduction, Literature Review, System Requirements & Analysis, "
            "System Design, Implementation, Testing, Results & Discussion, Conclusion & Future Scope. "
            "You can add or modify chapters based on the project type."
        )

    return f"""You are an expert academic document planner. Your job is to analyze the provided project information and create a detailed document structure (outline) for a final year project report / black book / thesis.

You MUST return valid JSON only. No markdown, no explanation, no code fences. Just the JSON object.

The JSON structure must be:
{{
  "title": "Project Title",
  "document_type": "Black Book / Synopsis / Thesis",
  "chapters": [
    {{
      "chapter_number": 1,
      "title": "Chapter Title",
      "page_allocation": <number>,
      "word_target": <number>,
      "sections": [
        {{
          "section_number": "1.1",
          "title": "Section Title",
          "description": "Brief description of what this section should cover",
          "has_code": false,
          "has_diagram_placeholder": false,
          "diagram_type": null
        }}
      ]
    }}
  ],
  "front_matter": {front_matter_json},
  "back_matter": {back_matter_json},
  "content_strategy": "elaborate" or "summarize" or "balanced",
  "total_content_pages": <number>,
  "total_pages": <number>
}}

CRITICAL RULES:
1. The total pages MUST equal the user's requested page count. This is the MOST important rule.
2. Front matter + chapters + back matter = total pages. The front_matter and back_matter above are FIXED — do NOT change them. Only adjust chapter page allocations.
3. You MUST have at most {max_chapters} chapters. Fewer is better for small documents.
4. {chapter_guidance}
5. Each chapter's word_target MUST equal page_allocation * WORDS_PER_PAGE (given below).
6. Distribute pages wisely across chapters based on the project complexity and available info.
7. If user info is less than needed, set content_strategy to "elaborate".
8. If user info is more than needed, set content_strategy to "summarize".
9. Include diagram placeholders sparingly — only 1-2 for small documents (<=15 pages), more for larger ones.
10. Include code sections in implementation chapters.
11. Each section description should be detailed enough to guide content generation later.
12. Do NOT over-allocate pages. The sum of all page_allocation fields across front_matter, chapters, and back_matter must EXACTLY equal the target page count."""


def _enforce_page_budget(
    plan: dict,
    target_pages: int,
    content_pages: int,
    front_matter: list[dict],
    back_matter: list[dict],
    tracker: ProcessTracker,
) -> dict:
    """
    Force the plan's page/word allocations to match the target exactly.
    The LLM often ignores page constraints — this corrects it deterministically.
    """
    # Override front/back matter with our calculated values
    plan["front_matter"] = front_matter
    plan["back_matter"] = back_matter

    chapters = plan.get("chapters", [])
    if not chapters:
        return plan

    # Cap chapter count
    max_ch = _get_max_chapters(target_pages)
    if len(chapters) > max_ch:
        tracker.log(f"   ⚠ Trimming chapters from {len(chapters)} to {max_ch}")
        chapters = chapters[:max_ch]
        # Renumber
        for i, ch in enumerate(chapters):
            ch["chapter_number"] = i + 1

    # Calculate total chapter pages the LLM allocated
    llm_total = sum(ch.get("page_allocation", 1) for ch in chapters)

    if llm_total != content_pages:
        tracker.log(f"   ⚠ Rescaling chapter pages: LLM gave {llm_total}, need {content_pages}")
        # Proportionally rescale, ensuring at least 1 page per chapter
        if llm_total > 0:
            scale = content_pages / llm_total
        else:
            scale = 1

        allocated = 0
        for i, ch in enumerate(chapters):
            if i == len(chapters) - 1:
                # Last chapter gets the remainder
                ch["page_allocation"] = max(1, content_pages - allocated)
            else:
                ch["page_allocation"] = max(1, round(ch.get("page_allocation", 1) * scale))
                allocated += ch["page_allocation"]

    # Fix word targets to match page allocations
    for ch in chapters:
        ch["word_target"] = ch["page_allocation"] * WORDS_PER_PAGE

    plan["chapters"] = chapters
    plan["total_content_pages"] = content_pages
    front_pages = sum(fm["page_allocation"] for fm in front_matter)
    back_pages = sum(bm["page_allocation"] for bm in back_matter)
    plan["total_pages"] = front_pages + content_pages + back_pages

    tracker.log(f"   ✅ Enforced budget: {len(chapters)} chapters, {content_pages} content pages, {plan['total_pages']} total")

    return plan


def create_document_plan(
    project_title: str,
    project_summary: str,
    project_code: str,
    tech_stack: str,
    target_pages: int,
    college_format: str,
    additional_info: str,
    tracker: ProcessTracker,
) -> dict:
    """
    Analyze user inputs and create a document plan.

    Returns:
        Document plan as a dictionary.
    """
    step_id = tracker.start_step("document_planning", "Analyzing inputs and creating document structure")

    # Calculate front/back matter pages scaled to target
    front_matter = _get_front_matter_plan(target_pages)
    back_matter = _get_back_matter_plan(target_pages)
    front_matter_pages = sum(fm["page_allocation"] for fm in front_matter)
    back_matter_pages = sum(bm["page_allocation"] for bm in back_matter)
    content_pages = max(1, target_pages - front_matter_pages - back_matter_pages)
    max_chapters = _get_max_chapters(target_pages)

    tracker.log(f"   Page budget: {front_matter_pages} front + {content_pages} content + {back_matter_pages} back = {target_pages}")

    user_prompt = f"""
Create a detailed document plan for the following project:

PROJECT TITLE: {project_title}

PROJECT SUMMARY:
{project_summary}

TECHNOLOGY STACK: {tech_stack}

PROJECT CODE (snippet/overview):
{project_code[:5000] if project_code else "No code provided"}

ADDITIONAL INFORMATION:
{additional_info if additional_info else "None"}

COLLEGE FORMAT REQUIREMENTS:
{college_format if college_format else "Standard format - no specific requirements"}

TARGET TOTAL PAGES: {target_pages}
FRONT MATTER PAGES (FIXED): {front_matter_pages}
BACK MATTER PAGES (FIXED): {back_matter_pages}
AVAILABLE CONTENT PAGES (for chapters): {content_pages}
MAXIMUM CHAPTERS ALLOWED: {max_chapters}
WORDS PER PAGE: {WORDS_PER_PAGE}
TOTAL CONTENT WORDS NEEDED: {content_pages * WORDS_PER_PAGE}

The user has provided approximately {len(project_summary.split())} words of summary and {len(project_code.split()) if project_code else 0} words/tokens of code.

CRITICAL: The sum of all chapter page_allocation values MUST equal EXACTLY {content_pages}.
The total word_target across all chapters MUST equal EXACTLY {content_pages * WORDS_PER_PAGE}.
You MUST NOT exceed {max_chapters} chapters.
"""

    try:
        # Plan JSON grows with chapter count: ~500 tokens per chapter + 1000 base
        estimated_plan_words = max(1, content_pages // 10) * 500 + 1000
        dynamic_max_tokens = calculate_max_tokens(word_target=estimated_plan_words, buffer_multiplier=2.0)

        system_prompt = _build_system_prompt(target_pages)

        result = call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.3,
            max_tokens=dynamic_max_tokens,
            model=PLANNER_MODEL,
        )

        # Parse the JSON response
        raw_content = result["content"].strip()

        # Strip code fences robustly (handles ```json, ```JSON, ``` etc.)
        import re
        if "```" in raw_content:
            match = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw_content, re.IGNORECASE)
            if match:
                raw_content = match.group(1).strip()

        # Extract JSON object if there's surrounding text
        json_match = re.search(r"\{[\s\S]*\}", raw_content)
        if json_match:
            raw_content = json_match.group(0)

        plan = json.loads(raw_content.strip())

        # ── Post-plan enforcement: force page/word budgets to match target ──
        plan = _enforce_page_budget(plan, target_pages, content_pages, front_matter, back_matter, tracker)

        tracker.complete_step(
            step_id,
            input_tokens=result["input_tokens"],
            output_tokens=result["output_tokens"],
            llm_calls=1,
        )
        tracker.set_document_plan(plan)

        return plan

    except json.JSONDecodeError as e:
        tracker.fail_step(step_id, f"JSON parse error: {str(e)}")
        raise ValueError(f"Failed to parse document plan: {str(e)}")
    except Exception as e:
        tracker.fail_step(step_id, str(e))
        raise

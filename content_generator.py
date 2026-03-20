"""
Content Generator - Generates chapter content using batch parallel LLM calls.
Each chapter is generated independently with its own context and page target.
"""
import asyncio
import json
from config import WORDS_PER_PAGE, BATCH_CONCURRENCY, calculate_max_tokens, GENERATOR_MODEL
from llm_client import batch_call_llm, call_llm
from tracker import ProcessTracker


CHAPTER_SYSTEM_PROMPT = """You are an expert academic writer specializing in final year project documentation. 
Write detailed, professional, academic-quality content for the specified chapter of a project report.

WRITING RULES:
1. Write in a formal, academic tone.
2. Use third person perspective (avoid "I", "we"). Use "the system", "the application", "this project".
3. Write EXACTLY the target word count specified. This is critical - do not write more or fewer words.
4. Structure content with clear headings and subheadings using these markers:
   - ## for main section headings (e.g., ## 1.1 Background)
   - ### for subsections (e.g., ### 1.1.1 Overview)
5. For code blocks, wrap them in ```language ... ``` markers.
6. For diagram placeholders, use: [DIAGRAM: diagram_type - Description of what the diagram should show]
   Example: [DIAGRAM: System Architecture - Shows the three-tier architecture with frontend, backend, and database layers]
7. For tables, use markdown table format:
   | Column 1 | Column 2 |
   |----------|----------|
   | Data     | Data     |
8. Be thorough and detailed. Include:
   - Technical explanations with depth
   - Real-world examples and comparisons
   - Advantages and disadvantages where relevant
   - Mathematical formulas if applicable (use plain text notation)
9. Do NOT include chapter title at the start (it will be added by the formatter).
10. Ensure all sections listed in the outline are covered.
11. Each paragraph should be 4-6 sentences long.
12. Use transitional phrases between sections.
"""

FRONT_MATTER_SYSTEM_PROMPT = """You are an expert academic writer. Generate the specified front matter section for a final year project report.
Write in formal academic language. Follow the exact format required for each section type.
Return ONLY the content text, no JSON or special formatting."""


def generate_front_matter(
    section_type: str,
    project_title: str,
    project_summary: str,
    student_name: str,
    college_name: str,
    guide_name: str,
    department: str,
    year: str,
    tracker: ProcessTracker,
) -> dict:
    """Generate front matter content (abstract, acknowledgment, etc.)."""
    step_id = tracker.start_step(
        f"front_matter_{section_type}",
        f"Generating {section_type}",
    )

    prompts = {
        "abstract": f"""Write an abstract (250-300 words) for the following project:
Title: {project_title}
Summary: {project_summary}

The abstract should cover: background, problem statement, methodology, key features, technology used, and conclusion.""",

        "acknowledgment": f"""Write an acknowledgment page for a final year project report.
Student: {student_name}
College: {college_name}
Guide/Mentor: {guide_name}
Department: {department}

Include gratitude to guide, HOD, college, family, and friends. Keep it formal and 200-250 words.""",
    }

    user_prompt = prompts.get(section_type, f"Generate {section_type} for project: {project_title}")

    try:
        result = call_llm(
            system_prompt=FRONT_MATTER_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.5,
            max_tokens=1024,
            model=GENERATOR_MODEL,
        )
        tracker.complete_step(
            step_id,
            input_tokens=result["input_tokens"],
            output_tokens=result["output_tokens"],
        )
        return {"type": section_type, "content": result["content"]}

    except Exception as e:
        tracker.fail_step(step_id, str(e))
        return {"type": section_type, "content": f"Error generating {section_type}: {str(e)}"}


async def generate_all_chapters(
    plan: dict,
    project_summary: str,
    project_code: str,
    tech_stack: str,
    additional_info: str,
    tracker: ProcessTracker,
) -> list[dict]:
    """
    Generate all chapter content in parallel batches.

    Returns:
        List of dicts: [{chapter_number, title, content, word_count, input_tokens, output_tokens}, ...]
    """
    step_id = tracker.start_step(
        "batch_content_generation",
        f"Generating {len(plan['chapters'])} chapters in parallel",
    )

    # Prepare batch calls
    calls = []
    for chapter in plan["chapters"]:
        sections_desc = "\n".join(
            f"  - {s['section_number']} {s['title']}: {s['description']}"
            + (f" [Include code examples]" if s.get("has_code") else "")
            + (
                f" [Include placeholder for {s.get('diagram_type', 'diagram')}]"
                if s.get("has_diagram_placeholder")
                else ""
            )
            for s in chapter["sections"]
        )

        user_prompt = f"""
PROJECT TITLE: {plan.get('title', 'Untitled Project')}
TECHNOLOGY STACK: {tech_stack}
CONTENT STRATEGY: {plan.get('content_strategy', 'balanced')}

PROJECT SUMMARY:
{project_summary}

PROJECT CODE (relevant portions):
{project_code[:3000] if project_code else "No code provided - generate representative examples based on the tech stack"}

ADDITIONAL CONTEXT:
{additional_info if additional_info else "None"}

---

CHAPTER TO WRITE: Chapter {chapter['chapter_number']} - {chapter['title']}
TARGET WORD COUNT: {chapter['word_target']} words (this is CRITICAL - write exactly this many words)
TARGET PAGES: {chapter['page_allocation']}

SECTIONS TO COVER:
{sections_desc}

Write the complete chapter content now. Remember to hit the target word count of {chapter['word_target']} words.
"""
        calls.append({
            "system_prompt": CHAPTER_SYSTEM_PROMPT,
            "user_prompt": user_prompt,
            "temperature": 0.7,
            "max_tokens": calculate_max_tokens(chapter["word_target"]),
            "model": GENERATOR_MODEL,
        })

    try:
        # Run batch generation
        results = await batch_call_llm(calls, concurrency=BATCH_CONCURRENCY)

        total_input_tokens = 0
        total_output_tokens = 0
        chapters_content = []

        for i, (chapter, result) in enumerate(zip(plan["chapters"], results)):
            total_input_tokens += result.get("input_tokens", 0)
            total_output_tokens += result.get("output_tokens", 0)

            content = result.get("content", "")
            word_count = len(content.split())

            chapters_content.append({
                "chapter_number": chapter["chapter_number"],
                "title": chapter["title"],
                "content": content,
                "word_count": word_count,
                "target_words": chapter["word_target"],
                "sections": chapter["sections"],
            })

        tracker.complete_step(
            step_id,
            input_tokens=total_input_tokens,
            output_tokens=total_output_tokens,
            llm_calls=len(calls),
        )

        return chapters_content

    except Exception as e:
        tracker.fail_step(step_id, str(e))
        raise


async def calibrate_content(
    chapters: list[dict],
    plan: dict,
    tracker: ProcessTracker,
) -> list[dict]:
    """
    Check generated content against page targets and adjust if needed.
    Re-generates chapters that are significantly off target.
    Also enforces total word budget across all chapters.
    """
    step_id = tracker.start_step(
        "content_calibration",
        "Checking content against page targets and adjusting",
    )

    # Calculate total word budget from plan
    total_target_words = sum(ch.get("word_target", 0) for ch in plan.get("chapters", []))
    total_actual_words = sum(ch["word_count"] for ch in chapters)
    total_deviation = (total_actual_words - total_target_words) / total_target_words if total_target_words > 0 else 0

    tracker.log(f"   Total words: {total_actual_words} / {total_target_words} target ({total_deviation:+.0%})")

    # If total content is way over budget, scale down all chapter targets proportionally
    if total_deviation > 0.15:
        # We need to shrink — recalculate targets so total matches budget
        scale_factor = total_target_words / total_actual_words
        tracker.log(f"   ⚠ Content {total_deviation:+.0%} over budget, scaling targets down (factor: {scale_factor:.2f})")
        for chapter in chapters:
            chapter["target_words"] = int(chapter["word_count"] * scale_factor)

    chapters_to_fix = []
    for idx, chapter in enumerate(chapters):
        target = chapter["target_words"]
        actual = chapter["word_count"]
        deviation = (actual - target) / target if target > 0 else 0

        # If more than 20% off target, regenerate
        if abs(deviation) > 0.20:
            if actual < target:
                instruction = f"EXPAND this content to exactly {target} words. Add more detail, examples, and explanations. Current word count: {actual}."
            else:
                instruction = f"CONDENSE this content to exactly {target} words. Keep the most important points and remove redundancy. Current word count: {actual}."

            tracker.log(f"   ⚠ Ch {chapter['chapter_number']}: {actual} words vs {target} target ({deviation:+.0%}) — will fix")

            chapters_to_fix.append({
                "system_prompt": f"""You are an academic content editor. {instruction}
Maintain the same structure and sections. Keep all headings.
Return the adjusted content only.""",
                "user_prompt": chapter["content"],
                "temperature": 0.5,
                "max_tokens": calculate_max_tokens(target),
                "model": GENERATOR_MODEL,
                "chapter_index": idx,
            })

    if chapters_to_fix:
        batch_calls = [
            {
                "system_prompt": c["system_prompt"],
                "user_prompt": c["user_prompt"],
                "temperature": c["temperature"],
                "max_tokens": c["max_tokens"],
            }
            for c in chapters_to_fix
        ]
        results = await batch_call_llm(batch_calls, concurrency=BATCH_CONCURRENCY)

        total_in = 0
        total_out = 0
        for fix_info, result in zip(chapters_to_fix, results):
            idx = fix_info["chapter_index"]
            if "error" not in result:
                chapters[idx]["content"] = result["content"]
                chapters[idx]["word_count"] = len(result["content"].split())
            total_in += result.get("input_tokens", 0)
            total_out += result.get("output_tokens", 0)

        tracker.complete_step(
            step_id,
            input_tokens=total_in,
            output_tokens=total_out,
            llm_calls=len(chapters_to_fix),
        )
    else:
        tracker.complete_step(step_id, input_tokens=0, output_tokens=0, llm_calls=0)

    # Final check
    final_words = sum(ch["word_count"] for ch in chapters)
    tracker.log(f"   Calibrated total: {final_words} words (target: {total_target_words})")

    return chapters

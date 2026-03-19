"""
Document Planner - Analyzes user inputs and creates a structured document plan.
Uses LLM to generate chapter outlines with page allocations.
"""
import json
from config import WORDS_PER_PAGE
from llm_client import call_llm
from tracker import ProcessTracker


PLANNER_SYSTEM_PROMPT = """You are an expert academic document planner. Your job is to analyze the provided project information and create a detailed document structure (outline) for a final year project report / black book / thesis.

You MUST return valid JSON only. No markdown, no explanation, no code fences. Just the JSON object.

The JSON structure must be:
{
  "title": "Project Title",
  "document_type": "Black Book / Synopsis / Thesis",
  "chapters": [
    {
      "chapter_number": 1,
      "title": "Chapter Title",
      "page_allocation": 10,
      "word_target": 3000,
      "sections": [
        {
          "section_number": "1.1",
          "title": "Section Title",
          "description": "Brief description of what this section should cover",
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
  "content_strategy": "elaborate" or "summarize" or "balanced",
  "total_content_pages": <number>,
  "total_pages": <number>
}

Rules:
1. The total pages MUST equal the user's requested page count.
2. Front matter + chapters + back matter = total pages.
3. Distribute pages wisely across chapters based on the project complexity and available info.
4. If user info is less than needed, set content_strategy to "elaborate" and plan for detailed explanations, examples, literature review, etc.
5. If user info is more than needed, set content_strategy to "summarize" and plan for concise but comprehensive coverage.
6. Include diagram placeholders where appropriate (system architecture, ER diagram, DFD, flowchart, use case diagram, class diagram, sequence diagram).
7. Include code sections in implementation chapters.
8. Standard chapters: Introduction, Literature Review, System Requirements & Analysis, System Design, Implementation, Testing, Results & Discussion, Conclusion & Future Scope.
9. You can add or modify chapters based on the project type.
10. Each section description should be detailed enough to guide content generation later.
"""


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

    # Calculate content pages (total minus front/back matter estimate)
    front_matter_pages = 9  # title + cert + ack + abstract + toc + list of figs + list of tables
    back_matter_estimate = max(5, int(target_pages * 0.05))  # ~5% for references + appendix
    content_pages = target_pages - front_matter_pages - back_matter_estimate

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
AVAILABLE CONTENT PAGES (for chapters): {content_pages}
WORDS PER PAGE: {WORDS_PER_PAGE}
TOTAL CONTENT WORDS NEEDED: {content_pages * WORDS_PER_PAGE}

The user has provided approximately {len(project_summary.split())} words of summary and {len(project_code.split()) if project_code else 0} words/tokens of code.

Create the document plan. Remember: total pages must equal {target_pages}.
"""

    try:
        result = call_llm(
            system_prompt=PLANNER_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.3,
            max_tokens=4096,
        )

        # Parse the JSON response
        content = result["content"].strip()
        # Remove code fences if present
        if content.startswith("```"):
            content = content.split("\n", 1)[1]
        if content.endswith("```"):
            content = content.rsplit("```", 1)[0]
        if content.startswith("json"):
            content = content[4:]

        plan = json.loads(content.strip())

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

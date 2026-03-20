"""
Configuration module for the Document Generator.
Loads environment variables and provides app-wide settings.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Anthropic Settings
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Model tiers:
# - PLANNER_MODEL   → complex reasoning (document plan, references)
# - GENERATOR_MODEL → bulk text generation (chapters, front matter, calibration)
PLANNER_MODEL   = os.getenv("ANTHROPIC_PLANNER_MODEL",   "claude-sonnet-4-6")
GENERATOR_MODEL = os.getenv("ANTHROPIC_GENERATOR_MODEL", "claude-haiku-4-5-20251001")

# Document Settings
MAX_PAGES = 250
MIN_PAGES = 10
WORDS_PER_PAGE = 210  # Approximate words per A4 page with 1.5 spacing, headings, tables, diagrams
LINES_PER_PAGE = 30

# Token Limits
DEFAULT_MAX_OUTPUT_TOKENS = 4096       # Default for simple calls
MAX_OUTPUT_TOKENS_PER_CALL = 8096      # Hard cap per call
MAX_INPUT_TOKENS_PER_CALL = 128000


def calculate_max_tokens(word_target: int = 0, buffer_multiplier: float = 1.5, default: int = DEFAULT_MAX_OUTPUT_TOKENS) -> int:
    """
    Dynamically calculate max_tokens based on word target.
    - 1 token ≈ 0.75 words, so tokens_needed = word_target / 0.75 = word_target * 1.33
    - Apply a buffer multiplier (default 1.5x) for safety
    - Clamp between default and MAX_OUTPUT_TOKENS_PER_CALL
    """
    if word_target <= 0:
        return default
    tokens_needed = int(word_target * 1.33 * buffer_multiplier)
    return max(default, min(tokens_needed, MAX_OUTPUT_TOKENS_PER_CALL))

# Batch Settings
BATCH_CONCURRENCY = 12  # Number of parallel LLM calls

# Document Formatting
DEFAULT_FONT = "Times New Roman"
HEADING1_SIZE = 16
HEADING2_SIZE = 14
HEADING3_SIZE = 12
BODY_SIZE = 12
CODE_FONT = "Consolas"
CODE_SIZE = 10
LINE_SPACING = 1.5
PAGE_MARGIN_INCHES = 1.0

# File Paths
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
TRACKING_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tracking")

# Create directories if they don't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TRACKING_DIR, exist_ok=True)

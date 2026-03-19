"""
Configuration module for the Document Generator.
Loads environment variables and provides app-wide settings.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Azure OpenAI Settings
AZURE_OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_VERSION = os.getenv("AZURE_OPENAI_VERSION", "2024-12-01-preview")
AZURE_DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME", "gpt-4.1-mini")

# Document Settings
MAX_PAGES = 250
MIN_PAGES = 10
WORDS_PER_PAGE = 300  # Approximate words per A4 page with standard formatting
LINES_PER_PAGE = 30

# Token Limits
MAX_OUTPUT_TOKENS_PER_CALL = 4096
MAX_INPUT_TOKENS_PER_CALL = 128000

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

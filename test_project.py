"""Test all project imports and verify setup."""
import sys
print(f"Python: {sys.version}\n")

tests = [
    ("config", "from config import AZURE_OPENAI_ENDPOINT, OUTPUT_DIR, TRACKING_DIR"),
    ("tracker", "from tracker import ProcessTracker"),
    ("llm_client", "from llm_client import get_llm, call_llm, count_tokens, batch_call_llm"),
    ("planner", "from planner import create_document_plan"),
    ("content_generator", "from content_generator import generate_all_chapters, generate_front_matter, calibrate_content"),
    ("doc_formatter", "from doc_formatter import DocumentFormatter"),
    ("pipeline", "from pipeline import run_pipeline, build_pipeline"),
    ("python-docx", "from docx import Document"),
    ("streamlit", "import streamlit"),
    ("tiktoken", "import tiktoken"),
    ("langgraph", "from langgraph.graph import StateGraph, START, END"),
    ("langchain-openai", "from langchain_openai import AzureChatOpenAI"),
    ("langchain-core", "from langchain_core.messages import HumanMessage, SystemMessage"),
]

passed = 0
failed = 0
for name, imp in tests:
    try:
        exec(imp)
        print(f"  ✓ {name}")
        passed += 1
    except Exception as e:
        print(f"  ✗ {name}: {e}")
        failed += 1

print(f"\n{'='*40}")
print(f"Results: {passed} passed, {failed} failed")

if failed == 0:
    print("\n✅ All imports working! Project is ready.")
else:
    print(f"\n❌ {failed} import(s) failed. Fix errors above.")

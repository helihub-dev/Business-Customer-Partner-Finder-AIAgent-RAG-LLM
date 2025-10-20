"""Configuration settings for AxleWave Discovery prototype."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
DOCS_DIR = DATA_DIR / "axlewave_docs"
VECTOR_STORE_DIR = DATA_DIR / "vector_store"
PROMPTS_DIR = PROJECT_ROOT / "prompts"

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")

# LLM Settings
DEFAULT_LLM_PROVIDER = "openai"
DEFAULT_MODEL = "gpt-4o-mini"
TEMPERATURE = 0.1
MAX_TOKENS = 4000

# Search Settings
MAX_SEARCH_RESULTS = 5
SEARCH_TIMEOUT = 60

# Agent Settings
MAX_COMPANIES_TO_RESEARCH = 10
TOP_N_RESULTS = 5

# Vector Store Settings
EMBEDDING_MODEL = "text-embedding-3-small"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Create directories if they don't exist
VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)
DOCS_DIR.mkdir(parents=True, exist_ok=True)

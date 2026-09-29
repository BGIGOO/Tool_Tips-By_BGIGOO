import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file
load_dotenv(BASE_DIR / ".env")

# API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

# Model Priority List (auto-fallback if a model encounters 503 high demand or 429 rate limit)
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite-preview")

MODEL_FALLBACKS = [
    DEFAULT_MODEL,
    "gemini-3.1-flash-lite-preview",
    "gemini-flash-latest",
    "gemini-3.8-flash",
    "gemini-3.5-flash-lite",
    "gemini-pro-latest",
]
# Remove duplicates while preserving order
MODEL_PRIORITY = list(dict.fromkeys(MODEL_FALLBACKS))

# Directories
TEMP_AUDIO_DIR = BASE_DIR / "temp_audio"
OUTPUTS_DIR = BASE_DIR / "outputs"

# Ensure directories exist
TEMP_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

# Processing parameters
MAX_RETRIES = 5
INITIAL_RETRY_DELAY = 2.0  # seconds

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project Root
BASE_DIR = Path(__file__).resolve().parent.parent

# API Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')

# Model Settings
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
GROQ_MODEL = os.getenv('GROQ_MODEL', 'llama-3.1-70b-versatile')

# Database
DATABASE_PATH = os.getenv('DATABASE_PATH', str(BASE_DIR / 'data' / 'studyai.db'))

# Generation Settings
MAX_TOKENS = int(os.getenv('MAX_TOKENS', 2000))
TEMPERATURE = float(os.getenv('TEMPERATURE', 0.7))
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Study Tool Defaults
DEFAULT_FLASHCARD_COUNT = 20
DEFAULT_QUIZ_COUNT = 10
DEFAULT_SUMMARY_LENGTH = 'medium'  # short, medium, long

# Supported File Types
SUPPORTED_EXTENSIONS = ['.pdf', '.txt', '.docx']

# Output Directory
OUTPUT_DIR = BASE_DIR / 'output'
OUTPUT_DIR.mkdir(exist_ok=True)

# Data Directory
DATA_DIR = BASE_DIR / 'data'
DATA_DIR.mkdir(exist_ok=True)

# Benchmarking Settings
BENCHMARK_METRICS = ['response_time', 'token_usage', 'cost', 'quality_score']

# API Provider Names
PROVIDERS = {
    'openai': 'OpenAI',
    'groq': 'Groq'
}

# Pricing (per 1M tokens)
PRICING = {
    'openai': {
        'gpt-3.5-turbo': {'input': 0.50, 'output': 1.50},
        'gpt-4': {'input': 30.00, 'output': 60.00},
        'gpt-4-turbo': {'input': 10.00, 'output': 30.00}
    },
    'groq': {
        'llama-3.1-70b-versatile': {'input': 0.59, 'output': 0.79},
        'llama-3.1-8b-instant': {'input': 0.05, 'output': 0.08},
        'mixtral-8x7b-32768': {'input': 0.24, 'output': 0.24}
    }
}

def validate_config():
    """Validate that all required configuration is present."""
    errors = []
    
    if not OPENAI_API_KEY:
        errors.append("OPENAI_API_KEY is not set")
    if not GROQ_API_KEY:
        errors.append("GROQ_API_KEY is not set")
    
    if errors:
        raise ValueError(f"Configuration errors: {', '.join(errors)}")
    
    return True

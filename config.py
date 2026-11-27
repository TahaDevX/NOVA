import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('OPENROUTER_API_KEY', '').strip()
MODEL = os.getenv('OPENROUTER_MODEL', 'google/gemini-2.5-flash').strip()
FALLBACK_MODEL = os.getenv('OPENROUTER_FALLBACK_MODEL', 'openai/gpt-4o-mini').strip()
HOST = os.getenv('APP_HOST', '0.0.0.0').strip()
PORT = int(os.getenv('APP_PORT', '8000'))

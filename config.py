import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:5000")
API_PREFIX = "/api"

ADMIN_USERNAME = os.getenv("API_ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("API_ADMIN_PASSWORD", "admin123")

DEFAULT_TIMEOUT = int(os.getenv("API_TIMEOUT", "10"))
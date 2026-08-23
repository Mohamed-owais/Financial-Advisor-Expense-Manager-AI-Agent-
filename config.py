"""
Financial Advisor MVP - Configuration File
Stores all settings, API keys, and constants
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============ DATABASE CONFIG ============
DATABASE_PATH = os.getenv("DATABASE_PATH", "expenses.db")

# ============ API KEYS ============
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GOOGLE_VISION_API_KEY = os.getenv("GOOGLE_VISION_API_KEY")

# ============ API SETTINGS ============
GROQ_MODEL = "openai/gpt-oss-120b" # Fast, free Groq model
GROQ_MAX_TOKENS = 500

# ============ OCR SETTINGS ============
MAX_IMAGE_SIZE_MB = 10
SUPPORTED_FORMATS = ["jpg", "jpeg", "png", "webp", "bmp"]

# ============ APP SETTINGS ============
APP_TITLE = "💰 Financial Advisor & Expense Manager"
APP_ICON = "💳"

# Categories for expense classification
EXPENSE_CATEGORIES = [
    "Food & Dining",
    "Transportation",
    "Entertainment",
    "Shopping",
    "Bills & Utilities",
    "Healthcare",
    "Education",
    "Travel",
    "Groceries",
    "Other"
]

# ============ VALIDATION ============
def validate_config():
    """Check if all required API keys are set"""
    missing = []
    
    if not GROQ_API_KEY:
        missing.append("GROQ_API_KEY")
    if not GOOGLE_VISION_API_KEY:
        missing.append("GOOGLE_VISION_API_KEY")
    
    if missing:
        print(f"⚠️  Warning: Missing env variables: {', '.join(missing)}")
        print("   Update your .env file with API keys")
    
    return len(missing) == 0

if __name__ == "__main__":
    validate_config()
    print("✅ Config loaded successfully")

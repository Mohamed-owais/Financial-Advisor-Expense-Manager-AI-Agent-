"""
Configuration for Financial Advisor MVP
Loads environment variables and sets up API keys
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================
# GROQ LLM Configuration
# ============================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "mixtral-8x7b-32768"  # Fast and capable model
GROQ_MAX_TOKENS = 1024
GROQ_TEMPERATURE = 0.3

# ============================================
# Google Vision API Configuration
# ============================================
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# ============================================
# Database Configuration
# ============================================
DATABASE_PATH = "expenses.db"
DATABASE_TIMEOUT = 10.0

# ============================================
# Validation
# ============================================
def validate_config():
    """Validate that all required configuration is present"""
    issues = []
    
    if not GROQ_API_KEY:
        issues.append("❌ GROQ_API_KEY not set in environment")
    else:
        print("✅ GROQ_API_KEY configured")
    
    if not GOOGLE_CREDENTIALS_PATH:
        issues.append("❌ GOOGLE_APPLICATION_CREDENTIALS not set in environment")
    elif not os.path.exists(GOOGLE_CREDENTIALS_PATH):
        issues.append(f"❌ GOOGLE_APPLICATION_CREDENTIALS file not found: {GOOGLE_CREDENTIALS_PATH}")
    else:
        print(f"✅ GOOGLE_APPLICATION_CREDENTIALS file found: {GOOGLE_CREDENTIALS_PATH}")
    
    return issues

# Run validation on import
if __name__ != "__main__":
    validation_issues = validate_config()
    for issue in validation_issues:
        print(issue)
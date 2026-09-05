import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API keys
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# Database
DATABASE_PATH = 'expenses.db'

# Validate keys
def validate_config():
    """Validate that required API keys are set"""
    if not GROQ_API_KEY:
        raise ValueError("❌ GROQ_API_KEY not found in .env file")
    
    print("✅ Configuration validated:")
    print(f"   - GROQ_API_KEY: {'Set' if GROQ_API_KEY else 'Missing'}")
    return True

if __name__ == "__main__":
    validate_config()
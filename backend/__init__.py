"""Backend package for Financial Advisor AI"""

from backend.ocr.engine import extract_text_from_image, initialize_reader
from backend.ai.analyzer import analyze_expense_with_groq
from backend.database.tracker import ExpenseTracker
from backend.config import GROQ_API_KEY, DATABASE_PATH, validate_config

__all__ = [
    'extract_text_from_image',
    'initialize_reader',
    'analyze_expense_with_groq',
    'ExpenseTracker',
    'GROQ_API_KEY',
    'DATABASE_PATH',
    'validate_config'
]
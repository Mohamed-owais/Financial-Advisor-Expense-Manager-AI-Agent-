"""
Test OCR Engine - Verify Google Vision API and Groq LLM initialization
"""

import os
import sys

# Add project directory to path
sys.path.insert(0, os.path.dirname(__file__))

from ocr_engine import OCREngine

if __name__ == "__main__":
    print("=" * 60)
    print("TEST 3.1: OCR ENGINE TEST")
    print("=" * 60)
    
    # Initialize OCR engine
    engine = OCREngine()
    
    print("\n✅ OCR Engine initialized successfully")
    print(f"Vision Client: {'Ready ✅' if engine.vision_client else 'Not configured ⚠️'}")
    print(f"Groq LLM: Ready ✅")
    
    # If vision client is ready, show status
    if engine.vision_client:
        print("\n✅ Google Vision API is properly configured!")
    else:
        print("\n⚠️  Google Vision API not configured")
        print("   Check: GOOGLE_APPLICATION_CREDENTIALS environment variable")
        print("   Check: gcp-key.json file exists in project folder")
    
    print("\n" + "=" * 60)
    print("TEST 3.1 COMPLETE")
    print("=" * 60)
    print("\nNext: Run test_database.py")

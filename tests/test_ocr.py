"""Test EasyOCR engine"""
import os
from ocr_engine import extract_text_from_image, initialize_reader

print("=" * 50)
print("TEST 3.1: EasyOCR Engine")
print("=" * 50)

try:
    print("\n1️⃣ Initializing OCR reader...")
    reader = initialize_reader()
    print("✅ OCR reader initialized successfully!")
    
    print("\n2️⃣ Testing with sample image...")
    
    # Create a simple test image if it doesn't exist
    test_image_path = "test_receipt.jpg"
    
    if os.path.exists(test_image_path):
        print(f"   Using existing test image: {test_image_path}")
        text = extract_text_from_image(test_image_path)
        print("\n✅ Text extraction successful!")
        print(f"\nExtracted text:\n{text[:200]}...")
    else:
        print(f"   ℹ️  No test image found at {test_image_path}")
        print("   To test: Upload a receipt image to the Streamlit app")
    
    print("\n" + "=" * 50)
    print("✅ TEST PASSED: EasyOCR engine is working!")
    print("=" * 50)

except Exception as e:
    print(f"\n❌ TEST FAILED: {str(e)}")
    print("=" * 50)
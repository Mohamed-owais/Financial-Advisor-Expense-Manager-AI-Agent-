import json
from PIL import Image
Image.ANTIALIAS = Image.Resampling.LANCZOS
import easyocr
import cv2
import os
from pathlib import Path

# Initialize reader once (loads model on first use)
reader = None

def initialize_reader():
    """Initialize EasyOCR reader"""
    global reader
    if reader is None:
        print("Loading OCR model (first time only, ~30 seconds)...")
        reader = easyocr.Reader(['en'], gpu=False)
    return reader

def extract_text_from_image(image_path):
    """
    Extract text from receipt image using EasyOCR
    
    Args:
        image_path (str): Path to image file
        
    Returns:
        str: Extracted text from image
    """
    try:
        # Initialize reader
        reader = initialize_reader()
        
        # Check if file exists
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not read image: {image_path}")
        
        # Extract text using EasyOCR
        print(f"Extracting text from {image_path}...")
        results = reader.readtext(image_path)
        
        # Combine all text
        extracted_text = '\n'.join([text[1] for text in results])
        
        if not extracted_text.strip():
            return "No text found in image"
        
        return extracted_text
        
    except Exception as e:
        print(f"❌ OCR Error: {str(e)}")
        raise

def analyze_expense_with_groq(receipt_text, groq_client):
    """
    Send extracted text to Groq LLM for analysis
    
    Args:
        receipt_text (str): Text extracted from receipt
        groq_client: Groq API client
        
    Returns:
        dict: Parsed expense details
    """
    try:
        prompt = f"""Extract from receipt: item name, amount in rupees (number only), category, date (YYYY-MM-DD), vendor name.
        Return ONLY this JSON format with NO other text:
        {{"item_name": "item", "amount": 0, "category": "Food", "date": "2024-09-05", "vendor": "shop"}}

        Receipt:
        {receipt_text}"""

        message = groq_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            max_tokens=256,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.choices[0].message.content.strip()
        print(f"DEBUG: Response = {response_text}")

        # Remove markdown if present
        response_text = message.choices[0].message.content.strip()
        print(f"DEBUG: Full response = '{response_text}'")

        if not response_text:
            return {
                "item_name": "Receipt",
                "amount": 0,
                "category": "Other",
                "date": "2024-09-05",
                "vendor": "Unknown"
            }

        # Remove markdown if present
        if '```' in response_text:
            response_text = response_text.split('```')[1]
            if response_text.startswith('json'):
                response_text = response_text[4:]

        response_text = response_text.strip()
        print(f"DEBUG: Cleaned response = '{response_text}'")

        # Parse JSON
        import json
        try:
            expense_data = json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"DEBUG: JSON error = {e}")
            return {
        "item_name": "Receipt",
        "amount": 0,
        "category": "Other",
        "date": "2024-09-05",
        "vendor": "Unknown"
    }
        
    except Exception as e:
        print(f"❌ Groq Analysis Error: {str(e)}")
        raise

# Test function
if __name__ == "__main__":
    test_image = "test_receipt.jpg"
    
    if os.path.exists(test_image):
        text = extract_text_from_image(test_image)
        print("✅ Extracted Text:")
        print(text)
    else:
        print(f"❌ Test image not found: {test_image}")
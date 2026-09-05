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
        prompt = f"""Analyze this receipt text and extract expense details.
Return ONLY a JSON object (no markdown, no backticks):

Receipt text:
{receipt_text}

Return JSON format:
{{"item_name": "...", "amount": 0.0, "category": "...", "date": "YYYY-MM-DD", "vendor": "..."}}

Categories: Food, Transport, Shopping, Entertainment, Utilities, Other"""

        message = groq_client.messages.create(
            model="mixtral-8x7b-32768",
            max_tokens=256,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = message.content[0].text.strip()
        
        # Parse JSON
        import json
        expense_data = json.loads(response_text)
        
        return expense_data
        
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
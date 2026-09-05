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
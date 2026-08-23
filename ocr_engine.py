"""
Financial Advisor MVP - OCR Engine
Extracts text and expense data from receipt/payment screenshots using Google Vision API
"""

import json
import os
import tempfile
from PIL import Image
import io
from google.cloud import vision
from groq import Groq
import config

class OCREngine:
    def __init__(self):
        """Initialize OCR and LLM engines"""
        # Initialize Google Vision API
        try:
            # Get credentials path from config
            credentials_path = config.GOOGLE_CREDENTIALS_PATH
            
            if not credentials_path:
                print("⚠️  GOOGLE_APPLICATION_CREDENTIALS not set in environment")
                self.vision_client = None
            elif not os.path.exists(credentials_path):
                print(f"⚠️  Google credentials file not found: {credentials_path}")
                self.vision_client = None
            else:
                # Set environment variable for Google client library
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
                
                # Initialize the Vision client
                self.vision_client = vision.ImageAnnotatorClient()
                print(f"✅ Google Vision Client initialized from: {credentials_path}")
        except Exception as e:
            print(f"⚠️  Warning: Could not initialize Google Vision: {e}")
            self.vision_client = None
        
        # Initialize Groq LLM for AI analysis
        try:
            self.groq_client = Groq(api_key=config.GROQ_API_KEY)
            print("✅ Groq LLM initialized")
        except Exception as e:
            print(f"⚠️  Warning: Could not initialize Groq: {e}")
            self.groq_client = None
    
    def extract_text_from_image(self, image_path):
        """
        Extract text from receipt image using Google Vision API
        
        Args:
            image_path: Path to receipt image
            
        Returns:
            dict: Extracted text and confidence scores
        """
        try:
            if not self.vision_client:
                return {
                    "success": False,
                    "text": "",
                    "error": "Google Vision API not configured"
                }
            
            # Read image file
            with open(image_path, 'rb') as image_file:
                content = image_file.read()
            
            image = vision.Image(content=content)
            
            # Call Google Vision API
            response = self.vision_client.text_detection(image=image)
            texts = response.text_annotations
            
            if texts:
                # First annotation is full text
                full_text = texts[0].description
                return {
                    "success": True,
                    "text": full_text,
                    "confidence": 0.95
                }
            else:
                return {
                    "success": False,
                    "text": "",
                    "error": "No text detected in image"
                }
                
        except Exception as e:
            return {
                "success": False,
                "text": "",
                "error": f"OCR Error: {str(e)}"
            }
    
    def analyze_expense_with_ai(self, receipt_text):
        """
        Use Groq LLM to analyze receipt text and extract expense details
        
        Args:
            receipt_text: Raw text from receipt
            
        Returns:
            dict: Parsed expense data (amount, vendor, category, date, etc.)
        """
        try:
            if not self.groq_client:
                return {
                    "success": False,
                    "error": "Groq LLM not configured"
                }
            
            # Create AI prompt for expense parsing
            prompt = f"""Analyze this receipt text and extract expense details. Return ONLY a JSON object with these fields:
- amount (numeric, e.g., 250.50)
- currency (e.g., "INR", "USD")
- vendor (store/restaurant name)
- category (one of: Food & Dining, Transportation, Entertainment, Shopping, Bills & Utilities, Healthcare, Education, Travel, Groceries, Other)
- items (list of 2-3 main items purchased)
- date (if visible, format as YYYY-MM-DD, else null)
- payment_method (cash, card, upi, online, unknown)
- notes (any special notes)

Receipt text:
{receipt_text}

Return ONLY valid JSON, no markdown formatting."""

            response = self.groq_client.chat.completions.create(
                model=config.GROQ_MODEL,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=config.GROQ_MAX_TOKENS,
                temperature=0.3
            )
            
            # Extract and parse response
            response_text = response.choices[0].message.content.strip()
            
            # Try to parse JSON
            try:
                # Remove markdown code blocks if present
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0].strip()
                
                expense_data = json.loads(response_text)
                expense_data["success"] = True
                return expense_data
            except json.JSONDecodeError:
                return {
                    "success": False,
                    "error": f"Could not parse AI response: {response_text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"AI Analysis Error: {str(e)}"
            }
    
    def process_receipt_image(self, image_path):
        """
        Complete pipeline: Extract text from image → Analyze with AI
        
        Args:
            image_path: Path to receipt image
            
        Returns:
            dict: Complete expense data or error
        """
        # Step 1: Extract text from image
        ocr_result = self.extract_text_from_image(image_path)
        
        if not ocr_result.get("success"):
            return ocr_result
        
        # Step 2: Analyze extracted text with AI
        expense_data = self.analyze_expense_with_ai(ocr_result["text"])
        
        # Add raw OCR text for reference
        expense_data["receipt_text"] = ocr_result["text"]
        
        return expense_data
    
    def process_from_bytes(self, image_bytes):
        """
        Process receipt from image bytes (for Streamlit file uploads)
        
        Args:
            image_bytes: Image file bytes
            
        Returns:
            dict: Complete expense data or error
        """
        try:
            # Save bytes to temporary file (works on Windows and Linux)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
                temp_file.write(image_bytes)
                temp_path = temp_file.name
            
            # Process the temporary file
            result = self.process_receipt_image(temp_path)
            
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            return result
        except Exception as e:
            return {
                "success": False,
                "error": f"Error processing image: {str(e)}"
            }


# Test the OCR engine
if __name__ == "__main__":
    engine = OCREngine()
    print("✅ OCR Engine initialized successfully")
    print(f"Vision Client: {'Ready' if engine.vision_client else 'Not configured'}")
    print(f"Groq LLM: {'Ready' if engine.groq_client else 'Not configured'}")
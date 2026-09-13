import json

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
        prompt = f"""From this receipt, extract: item name, amount (₹), category, date, vendor.
Categories: Food, Transport, Shopping, Entertainment, Utilities, Healthcare, Education, Other.

Receipt text:
{receipt_text}

Return ONLY JSON (no markdown):
{{"item_name": "item", "amount": 100, "category": "Food", "date": "2024-09-05", "vendor": "shop"}}"""
        message = groq_client.chat.completions.create(
            model="groq/compound-mini",
            max_tokens=256,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.choices[0].message.content.strip()
        print(f"DEBUG: Response length = {len(response_text)}")
        print(f"DEBUG: Response content = {repr(response_text)}")
        print(f"DEBUG: Full response = '{response_text}'")

        if not response_text:
            return {
                "item_name": "Receipt",
                "amount": 0,
                "category": "Other",
                "date": "2024-09-05",
                "vendor": "Unknown",
                "confidence": 0
            }

        # Remove markdown if present
        if '```' in response_text:
            response_text = response_text.split('```')[1]
            if response_text.startswith('json'):
                response_text = response_text[4:]

        response_text = response_text.strip()
        print(f"DEBUG: Cleaned response = '{response_text}'")

        # Parse JSON
        try:
            expense_data = json.loads(response_text)
            if isinstance(expense_data, list):
             expense_data = expense_data[0]
        except json.JSONDecodeError as e:
            print(f"DEBUG: JSON error = {e}")
            return {
                "item_name": "Receipt",
                "amount": 0,
                "category": "Other",
                "date": "2024-09-05",
                "vendor": "Unknown",
                "confidence": 0
            }
        
        return expense_data
        
    except Exception as e:
        print(f"❌ Groq Analysis Error: {str(e)}")
        raise
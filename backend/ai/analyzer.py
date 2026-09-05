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
        
        return expense_data
        
    except Exception as e:
        print(f"❌ Groq Analysis Error: {str(e)}")
        raise
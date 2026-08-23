"""
Test Groq LLM - Verify API connectivity and response quality
"""

import os
import sys

# Add project directory to path
sys.path.insert(0, os.path.dirname(__file__))

from groq import Groq
import config

if __name__ == "__main__":
    print("=" * 60)
    print("TEST 3.3: GROQ LLM TEST")
    print("=" * 60)
    
    # Check if API key is set
    api_key = config.GROQ_API_KEY
    if not api_key:
        print("\n❌ GROQ_API_KEY not found in config")
        print("   Check: .env file or GROQ_API_KEY environment variable")
        sys.exit(1)
    
    print("\n✅ Groq API key found")
    
    # Initialize Groq client
    try:
        client = Groq(api_key=api_key)
        print("✅ Groq client initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Groq client: {e}")
        sys.exit(1)
    
    # Test with a simple expense analysis prompt
    print("\n📝 Sending test prompt to Groq LLM...")
    
    test_prompt = """Analyze this receipt text and extract expense details. Return ONLY a JSON object:

Receipt text:
Starbucks Coffee
Latte: 250 INR
Date: 2026-08-23

Return ONLY valid JSON with fields: amount, currency, vendor, category, date"""
    
    try:
        response = client.chat.completions.create(
            model=config.GROQ_MODEL,
            messages=[
                {"role": "user", "content": test_prompt}
            ],
            max_tokens=config.GROQ_MAX_TOKENS,
            temperature=0.3
        )
        
        result = response.choices[0].message.content.strip()
        print("\n✅ Groq LLM Response:")
        print("-" * 60)
        print(result)
        print("-" * 60)
        
        # Check if response looks valid
        if "{" in result and "}" in result:
            print("\n✅ Response appears to be valid JSON")
        else:
            print("\n⚠️  Response may not be valid JSON")
            
    except Exception as e:
        print(f"\n❌ Error calling Groq API: {e}")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("TEST 3.3 COMPLETE")
    print("=" * 60)
    print("\nNext: Run test_complete_flow.py")

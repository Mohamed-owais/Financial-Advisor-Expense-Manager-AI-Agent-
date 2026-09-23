import os
from groq import Groq

api_key = os.getenv("GROQ_API_KEY")
print(f"API Key found: {api_key[:20]}..." if api_key else "No API key")

client = Groq(api_key=api_key)

try:
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": "Say hello"}],
        max_tokens=10
    )
    print("✅ API Key works!")
    print(f"Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"❌ Error: {e}")
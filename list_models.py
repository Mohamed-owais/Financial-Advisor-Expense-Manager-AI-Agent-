import os
from groq import Groq

api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)

try:
    models = client.models.list()
    print("Available models for your account:")
    for model in models.data:
        print(f"  - {model.id}")
except Exception as e:
    print(f"Error: {e}")
import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_financial_advice(user_profile: dict) -> str:
    """
    Generate financial advice based on user spending patterns.
    """
    
    # Format expenses nicely
    expenses_text = "\n".join([f"- {cat}: ₹{amount}" for cat, amount in user_profile['top_expenses'].items()])
    
    prompt = f"""You are a friendly financial advisor for Indians. Based on this profile, give 3-4 specific, actionable advice points.

USER PROFILE:
Monthly Income: ₹{user_profile['monthly_income']:,.0f}
Monthly Spending: ₹{user_profile['monthly_budget']:,.0f}

Top Expenses:
{expenses_text}

Goal: {user_profile['savings_goal']}

IMPORTANT: 
- Give practical advice for Indian middle-class people
- Mention Indian financial products (PPF, SIP, ELSS)
- Keep it simple and actionable

Your advice:"""
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=500,
        temperature=0.7
    )
    
    return response.choices[0].message.content


def get_guru_comparison(top_expenses: dict, guru_name: str = "Ramit Sethi") -> str:
    """
    Compare spending against financial guru principles.
    """
    
    expenses_text = "\n".join([f"- {cat}: ₹{amount}" for cat, amount in top_expenses.items()])
    
    prompt = f"""You are analyzing someone's spending habits using {guru_name}'s financial philosophy.

Spending Pattern:
{expenses_text}

Using {guru_name}'s principles, answer:
1. Are they following {guru_name}'s advice? How?
2. What would {guru_name} suggest to improve?
3. Give 2-3 specific actionable tips.

Keep it concise and practical."""
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=400,
        temperature=0.7
    )
    
    return response.choices[0].message.content


# TEST FUNCTION
if __name__ == "__main__":
    print("🧪 Testing Groq Integration...\n")
    
    test_profile = {
        "monthly_income": 50000,
        "top_expenses": {
            "Food": 8000,
            "Transport": 3000,
            "Entertainment": 2000,
            "Utilities": 1500,
            "Shopping": 5000
        },
        "monthly_budget": 19500,
        "savings_goal": "emergency fund"
    }
    
    print("📊 Getting financial advice...")
    advice = get_financial_advice(test_profile)
    print("\n✅ ADVICE:\n")
    print(advice)
    
    print("\n" + "="*60 + "\n")
    
    print("📚 Getting guru comparison...")
    guru_advice = get_guru_comparison(test_profile['top_expenses'], "Ramit Sethi")
    print("\n✅ GURU COMPARISON:\n")
    print(guru_advice)
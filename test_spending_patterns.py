import json
from datetime import datetime, timedelta
import random

def generate_spending_pattern(pattern_type, num_months=3):
    """Generate realistic spending patterns for testing"""
    
    patterns = {
        "student_budget": {
            "food": (2000, 4000),
            "entertainment": (1000, 2000),
            "shopping": (500, 1500),
            "utilities": (1000, 1500),
            "transport": (1500, 2500),
        },
        "saving_focused": {
            "food": (3000, 5000),
            "entertainment": (500, 1000),
            "shopping": (200, 500),
            "utilities": (2000, 3000),
            "transport": (2000, 3000),
            "savings": (5000, 10000),
        },
        "high_spender": {
            "food": (10000, 15000),
            "entertainment": (5000, 10000),
            "shopping": (8000, 15000),
            "utilities": (3000, 5000),
            "transport": (5000, 8000),
        },
        "balanced": {
            "food": (5000, 7000),
            "entertainment": (2000, 3000),
            "shopping": (2000, 3000),
            "utilities": (2000, 3000),
            "transport": (2000, 4000),
            "savings": (2000, 5000),
        }
    }
    
    spending_data = []
    base_date = datetime.now() - timedelta(days=90)
    
    for month in range(num_months):
        month_total = 0
        for category, (min_val, max_val) in patterns[pattern_type].items():
            for _ in range(random.randint(3, 4)):
                amount = random.randint(min_val, max_val) / random.randint(2, 4)
                date = base_date + timedelta(days=month*30 + random.randint(0, 28))
                
                spending_data.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "category": category,
                    "amount": round(amount, 2),
                    "description": f"{category} expense"
                })
                month_total += amount
        
        print(f"Month {month+1} total ({pattern_type}): ₹{month_total:.2f}")
    
    return spending_data

if __name__ == "__main__":
    patterns = ["student_budget", "saving_focused", "high_spender", "balanced"]
    
    for pattern in patterns:
        print(f"\n{'='*50}")
        print(f"Pattern: {pattern.upper()}")
        print('='*50)
        data = generate_spending_pattern(pattern)
        
        with open(f"test_data_{pattern}.json", "w") as f:
            json.dump(data, f, indent=2)
        print(f"✅ Saved {len(data)} transactions to test_data_{pattern}.json")
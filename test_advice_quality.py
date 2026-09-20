import json
import time
import os
from datetime import datetime
from groq import Groq

class AdviceQualityTester:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("❌ GROQ_API_KEY not found in .env file")
            exit(1)
        self.client = Groq(api_key=api_key)
        self.results = []
    
    def calculate_spending_summary(self, transactions):
        """Summarize spending by category"""
        summary = {}
        for tx in transactions:
            cat = tx["category"]
            summary[cat] = summary.get(cat, 0) + tx["amount"]
        return summary
    
    def generate_advice(self, spending_summary, pattern_name):
        """Generate advice and measure quality"""
        
        prompt = f"""Based on this spending pattern ({pattern_name}):
{json.dumps(spending_summary, indent=2)}

Give 3 specific financial advice points:
1. How to save more money (exact amounts in rupees)
2. Which category to reduce spending most
3. One universally-applicable investment strategy

STRICT RULES - DO NOT BREAK:
- ONLY recommend: ELSS mutual funds, PPF (Public Provident Fund), or generic SIP
- ELSS has 3-year mandatory lock-in (NOT 12 months)
- Section 80C allows UP TO ₹1.5 lakh deduction per year (NOT 80%)
- PPF limit: ₹1.5 lakh per financial year
- NEVER recommend: Sukanya Samriddhi, Senior Citizens Savings Scheme, or any scheme requiring specific demographics
- Investment recommendation must NOT exceed total savings freed up from step 1
- Be extremely specific: use exact ₹ amounts, percentages
- End with: "Disclaimer: This is educational information only, not certified financial advice."
- Keep response under 300 words"""
        start_time = time.time()
        
        try:
            response = self.client.chat.completions.create(
                model="groq/compound-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.3
            )
            
            elapsed = time.time() - start_time
            advice = response.choices[0].message.content
            
            result = {
                "pattern": pattern_name,
                "advice": advice,
                "response_time_sec": round(elapsed, 2),
                "tokens_used": response.usage.completion_tokens,
                "quality_score": self.score_advice(advice),
                "timestamp": datetime.now().isoformat()
            }
            
            self.results.append(result)
            return result
        
        except Exception as e:
            elapsed = time.time() - start_time
            error_result = {
                "pattern": pattern_name,
                "error": str(e),
                "response_time_sec": round(elapsed, 2)
            }
            self.results.append(error_result)
            return error_result
    
    def score_advice(self, advice_text):
        """Score advice quality (0-100)"""
        score = 0
        
        # Check for currency amounts
        if "₹" in advice_text or "Rs" in advice_text:
            score += 25
        
        # Check for time frames
        if any(word in advice_text.lower() for word in ["month", "year", "week"]):
            score += 20
        
        # Check for actionable verbs
        actions = ["increase", "reduce", "allocate", "invest", "save", "track", "limit"]
        action_count = sum(1 for action in actions if action in advice_text.lower())
        score += min(action_count * 15, 25)
        
        # Check for specific categories
        categories = ["food", "entertainment", "savings", "investment", "shopping", "utilities"]
        cat_count = sum(1 for cat in categories if cat in advice_text.lower())
        score += min(cat_count * 8, 30)
        
        return min(score, 100)
    
    def print_results(self):
        """Print formatted results"""
        print("\n" + "="*80)
        print("ADVICE QUALITY TEST RESULTS")
        print("="*80)
        
        for result in self.results:
            if "error" in result:
                print(f"\n❌ {result['pattern']}: ERROR - {result['error']}")
                continue
            
            print(f"\n✅ Pattern: {result['pattern']}")
            print(f"   Response Time: {result['response_time_sec']}s")
            print(f"   Tokens Used: {result['tokens_used']}")
            print(f"   Quality Score: {result['quality_score']}/100")
            print(f"\n   Advice:\n   {result['advice']}\n")
        
        # Summary stats
        successful = [r for r in self.results if "error" not in r]
        if successful:
            avg_time = sum(r["response_time_sec"] for r in successful) / len(successful)
            avg_quality = sum(r["quality_score"] for r in successful) / len(successful)
            
            print(f"\n{'='*80}")
            print(f"SUMMARY:")
            print(f"  Total Tests: {len(self.results)}")
            print(f"  Successful: {len(successful)}")
            print(f"  Avg Response Time: {avg_time:.2f}s (target: <5s) {'✅' if avg_time < 5 else '⚠️'}")
            print(f"  Avg Quality Score: {avg_quality:.1f}/100 (target: >80) {'✅' if avg_quality > 80 else '⚠️'}")
            print(f"{'='*80}\n")
    
    def save_results(self, filename="test_results.json"):
        """Save results to JSON"""
        with open(filename, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"✅ Results saved to {filename}\n")

if __name__ == "__main__":
    print("Starting Advice Quality Tests...\n")
    
    tester = AdviceQualityTester()
    patterns = ["student_budget", "saving_focused", "high_spender", "balanced"]
    
    for i, pattern in enumerate(patterns, 1):
        test_file = f"test_data_{pattern}.json"
        
        try:
            with open(test_file, "r") as f:
                transactions = json.load(f)
        except FileNotFoundError:
            print(f"⚠️ File not found: {test_file}")
            continue
        
        print(f"[{i}/4] Testing pattern: {pattern}...")
        summary = tester.calculate_spending_summary(transactions)
        result = tester.generate_advice(summary, pattern)
        
        if "error" not in result:
            print(f"      ✓ Response time: {result['response_time_sec']}s")
            print(f"      ✓ Quality score: {result['quality_score']}/100\n")
    
    tester.print_results()
    tester.save_results()
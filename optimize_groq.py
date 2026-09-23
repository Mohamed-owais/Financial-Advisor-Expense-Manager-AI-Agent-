import json
import time
import os
from groq import Groq

class GroqOptimizer:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("❌ GROQ_API_KEY not found")
            exit(1)
        self.client = Groq(api_key=api_key)
        self.results = []
    
    def test_settings(self, temperature, max_tokens, test_pattern_file):
        """Test a specific temperature/token combination"""
        
        with open(test_pattern_file, "r") as f:
            transactions = json.load(f)
        
        # Calculate summary
        summary = {}
        for tx in transactions:
            cat = tx["category"]
            summary[cat] = summary.get(cat, 0) + tx["amount"]
        
        prompt = f"""Based on this spending ({list(summary.keys())[0]} pattern):
{json.dumps(summary, indent=2)}

Give 3 specific financial advice points:
1. How to save more money (exact amounts in rupees)
2. Which category to reduce spending most
3. One universally-applicable investment strategy

STRICT RULES:
- ELSS has 3-year mandatory lock-in
- Section 80C allows UP TO ₹1.5 lakh deduction per year
- PPF limit: ₹1.5 lakh per financial year
- Investment must NOT exceed total savings from step 1
- End with: "Disclaimer: This is educational information only, not certified financial advice."
- Keep response under 300 words"""
        
        start_time = time.time()
        
        try:
            response = self.client.chat.completions.create(
                model="qwen/qwen3.8-27b",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            elapsed = time.time() - start_time
            advice = response.choices[0].message.content
            tokens = response.usage.completion_tokens
            
            result = {
                "temperature": temperature,
                "max_tokens": max_tokens,
                "response_time": round(elapsed, 2),
                "tokens_used": tokens,
                "advice_length": len(advice),
                "has_disclaimer": "disclaimer" in advice.lower(),
                "has_amounts": "₹" in advice,
                "status": "success"
            }
            
            self.results.append(result)
            return result
        
        except Exception as e:
            result = {
                "temperature": temperature,
                "max_tokens": max_tokens,
                "error": str(e),
                "status": "failed"
            }
            self.results.append(result)
            return result
    
    def print_results(self):
        """Print optimization results"""
        print("\n" + "="*100)
        print("GROQ API OPTIMIZATION RESULTS")
        print("="*100)
        print(f"{'Temp':<8} {'Tokens':<10} {'Time (s)':<10} {'Used':<8} {'Length':<10} {'Disclaimer':<12} {'Amounts':<10} {'Status':<10}")
        print("-"*100)
        
        for r in self.results:
            if r["status"] == "failed":
                print(f"{r['temperature']:<8} {r['max_tokens']:<10} {'ERROR':<10} - - - - {r['status']:<10}")
            else:
                print(f"{r['temperature']:<8} {r['max_tokens']:<10} {r['response_time']:<10} {r['tokens_used']:<8} {r['advice_length']:<10} {'✅' if r['has_disclaimer'] else '❌':<12} {'✅' if r['has_amounts'] else '❌':<10} {r['status']:<10}")
        
        print("="*100)
        print("\nRECOMMENDATION:")
        successful = [r for r in self.results if r["status"] == "success"]
        
        if successful:
            # Find best balance of speed + quality
            best = min(successful, key=lambda x: x["response_time"])
            print(f"\n⭐ BEST FOR SPEED:")
            print(f"   Temperature: {best['temperature']}")
            print(f"   Max tokens: {best['max_tokens']}")
            print(f"   Response time: {best['response_time']}s")
            
            # Find best for consistency
            best_quality = [r for r in successful if r['has_disclaimer'] and r['has_amounts']]
            if best_quality:
                best_q = min(best_quality, key=lambda x: x["response_time"])
                print(f"\n⭐ BEST FOR QUALITY + SPEED:")
                print(f"   Temperature: {best_q['temperature']}")
                print(f"   Max tokens: {best_q['max_tokens']}")
                print(f"   Response time: {best_q['response_time']}s")
        print()

if __name__ == "__main__":
    print("Starting Groq optimization tests...\n")
    
    optimizer = GroqOptimizer()
    
    # Test matrix: different temperatures and max_tokens
    settings = [
        (0.2, 250),   # Low temp, low tokens (fast, rigid)
        (0.3, 300),   # Recommended
        (0.5, 300),   # Medium temp
        (0.7, 350),   # Higher temp, more tokens
    ]
    
    test_file = "test_data_balanced.json"
    
    print(f"Testing with: {test_file}\n")
    
    for temp, tokens in settings:
        print(f"Testing temperature={temp}, max_tokens={tokens}...")
        result = optimizer.test_settings(temp, tokens, test_file)
        
        if result["status"] == "success":
            print(f"  ✓ {result['response_time']}s, {result['tokens_used']} tokens\n")
        else:
            print(f"  ✗ Failed\n")
    
    optimizer.print_results()
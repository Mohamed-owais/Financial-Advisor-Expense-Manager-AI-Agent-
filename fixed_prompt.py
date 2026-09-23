# Better prompt that prevents arithmetic errors

IMPROVED_PROMPT = """Based on this spending pattern:
{spending_summary}

Give 3 specific financial advice points:

1. How to save more money (exact amounts in rupees)
   - List each category reduction
   - Show calculation: category × percentage = savings
   - Total all savings

2. Which category to reduce spending most
   - Name the single highest category
   - Explain why it's the best to cut

3. One universally-applicable investment strategy
   - MUST match total savings from step 1 exactly
   - If monthly savings: recommend monthly investment amounts
   - If annual savings: recommend annual investment amounts
   - NO MIXING monthly and annual figures
   - Show: "Total savings: ₹X → Investment: ₹Y (where Y = X)"
   - ELSS: 3-year lock-in, eligible for Section 80C (up to ₹1.5L/year)
   - PPF: ₹1.5L per financial year limit

CRITICAL RULES:
- Every number must add up correctly
- Never include implementation tips with new calculations
- If step 1 says monthly, step 3 must be monthly
- If step 1 says annual, step 3 must be annual
- Always show: "Savings freed up: ₹X → Investment recommended: ₹X"
- End with: "Disclaimer: This is educational information only, not certified financial advice."
- Keep response under 300 words"""

print("Improved prompt ready.")
print("\nKey changes:")
print("✓ Explicit requirement: savings must equal investment")
print("✓ Forbid mixing monthly/annual")
print("✓ Remove implementation tips (source of math errors)")
print("✓ Force verification: 'Savings ₹X → Investment ₹X'")
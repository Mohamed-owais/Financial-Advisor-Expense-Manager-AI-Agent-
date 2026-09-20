from advice_validator import AdviceValidator
import json

validator = AdviceValidator()

# Load the test results
with open("test_results.json", "r") as f:
    results = json.load(f)

print("="*80)
print("VALIDATING ADVICE OUTPUTS")
print("="*80)

total_score_adjustment = 0

for result in results:
    if "error" in result:
        continue
    
    pattern = result["pattern"]
    advice = result["advice"]
    original_score = result["quality_score"]
    
    validation = validator.validate(advice)
    
    print(f"\n✅ {pattern}")
    print(f"   Original Score: {original_score}/100")
    
    if validation["is_valid"]:
        print(f"   Validation: PASS ✅")
        print(f"   Adjusted Score: {original_score}/100")
    else:
        adjusted = max(0, original_score + validation["score_adjustment"])
        print(f"   Validation: FAIL ❌")
        print(f"   Errors: {validation['errors']}")
        print(f"   Adjusted Score: {adjusted}/100")
        total_score_adjustment += validation["score_adjustment"]

print(f"\n{'='*80}")
print(f"VALIDATION SUMMARY")
print(f"Total patterns validated: {len([r for r in results if 'error' not in r])}")
print(f"All passed: {'YES ✅' if total_score_adjustment == 0 else 'NO ❌'}")
print(f"{'='*80}\n")
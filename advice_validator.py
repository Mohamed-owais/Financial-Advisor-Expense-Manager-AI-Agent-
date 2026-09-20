import re

class AdviceValidator:
    """Validates LLM advice output for accuracy, compliance, and formatting"""
    
    PROBLEMATIC_SCHEMES = [
        "sukanya samriddhi",
        "senior citizens savings scheme",
        "ssy",
        "scss"
    ]
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate(self, advice_text):
        """Run all validation checks"""
        self.errors = []
        self.warnings = []
        
        self.check_demographic_assumptions(advice_text)
        self.check_formatting(advice_text)
        self.check_disclaimer(advice_text)
        self.check_specificity(advice_text)
        
        return {
            "is_valid": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings,
            "score_adjustment": -5 * len(self.errors) + (-2 * len(self.warnings))
        }
    
    def check_demographic_assumptions(self, text):
        """Check for demographic-gated scheme recommendations without context"""
        text_lower = text.lower()
        
        for scheme in self.PROBLEMATIC_SCHEMES:
            if scheme in text_lower:
                self.errors.append(
                    f"❌ Recommends '{scheme}' without demographic context. "
                    f"This scheme requires specific conditions (e.g., daughter <10 years). "
                    f"Use ELSS or PPF instead."
                )
    
    def check_formatting(self, text):
        """Check for unicode/formatting issues"""
        # Check for non-breaking spaces
        if '\xa0' in text or '\u202f' in text:
            self.warnings.append(
                "⚠️ Non-breaking spaces detected. May cause rendering issues. "
                "Replace with regular spaces."
            )
        
        # Check for weird hyphens
        if '‑' in text or '–' in text:
            self.warnings.append(
                "⚠️ Non-standard hyphens detected. Use regular hyphen (-) instead."
            )
    
    def check_disclaimer(self, text):
        """Check for legal disclaimer"""
        disclaimer_keywords = [
            "disclaimer",
            "educational",
            "not financial advice",
            "consult a professional"
        ]
        
        has_disclaimer = any(keyword in text.lower() for keyword in disclaimer_keywords)
        
        if not has_disclaimer:
            self.errors.append(
                "❌ Missing legal disclaimer. Add: "
                "'Disclaimer: This is educational information only, not certified financial advice.'"
            )
    
    def check_specificity(self, text):
        """Verify advice is specific to the spending pattern"""
        specificity_markers = ["₹", "rs", "%", "reduce", "increase", "save"]
        marker_count = sum(text.lower().count(marker) for marker in specificity_markers)
        
        if marker_count < 5:
            self.warnings.append(
                "⚠️ Advice lacks specificity. Include exact amounts and percentages."
            )

if __name__ == "__main__":
    # Test the validator
    validator = AdviceValidator()
    
    test_advice = """
    Reduce entertainment by ₹2,000 per month.
    Start an SIP in a diversified fund.
    Consider Sukanya Samriddhi Yojana if applicable.
    """
    
    result = validator.validate(test_advice)
    
    print("Validation Results:")
    print(f"Valid: {result['is_valid']}")
    print(f"Errors: {result['errors']}")
    print(f"Warnings: {result['warnings']}")
    print(f"Score adjustment: {result['score_adjustment']}")
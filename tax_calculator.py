class IncomeTaxCalculator:
    """Indian Income Tax Calculator (FY 2024-25)"""
    
    TAX_SLABS = [
        (250000, 0),           # 0-2.5L: 0%
        (500000, 0.05),        # 2.5-5L: 5%
        (1000000, 0.20),       # 5-10L: 20%
        (float('inf'), 0.30)   # 10L+: 30%
    ]
    
    DEDUCTIONS = {
        "80C": 150000,         # ELSS, PPF, LIC, etc
        "80D": 50000,          # Health insurance
        "80E": 50000,          # Education loan
        "80CCD": 50000,        # NPS
    }
    
    def __init__(self, annual_income):
        self.annual_income = annual_income
        self.taxable_income = annual_income
    
    def apply_deduction(self, deduction_type, amount):
        """Apply tax deduction"""
        if deduction_type in self.DEDUCTIONS:
            max_ded = self.DEDUCTIONS[deduction_type]
            ded = min(amount, max_ded)
            self.taxable_income -= ded
            return ded
        return 0
    
    def calculate_tax(self):
        """Calculate income tax based on slabs"""
        tax = 0
        remaining = self.taxable_income
        
        for slab_limit, rate in self.TAX_SLABS:
            if remaining <= 0:
                break
            taxable_in_slab = min(remaining, slab_limit)
            tax += taxable_in_slab * rate
            remaining -= taxable_in_slab
        
        return tax
    
    def get_summary(self):
        """Return complete tax calculation"""
        tax = self.calculate_tax()
        cess = tax * 0.04  # 4% cess
        total_tax = tax + cess
        
        return {
            "gross_income": self.annual_income,
            "taxable_income": self.taxable_income,
            "income_tax": round(tax, 2),
            "cess_4pct": round(cess, 2),
            "total_tax": round(total_tax, 2),
            "net_income": round(self.annual_income - total_tax, 2)
        }
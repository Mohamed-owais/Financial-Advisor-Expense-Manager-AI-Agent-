class IncomeTaxCalculator:
    """Indian Income Tax Calculator (FY 2024-25)"""

    TAX_SLABS = [
        (300000, 0),           # 0-3L: 0%
        (600000, 0.05),        # 3-6L: 5%
        (900000, 0.20),        # 6-9L: 20%
        (1200000, 0.30),       # 9-12L: 30%
        (float('inf'), 0.30)   # 12L+: 30%
    ]

    DEDUCTIONS = {
        "80C": 150000,
        "80D": 50000,
        "80E": 50000,
        "80CCD": 50000,
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
        previous_limit = 0

        for slab_limit, rate in self.TAX_SLABS:
            if self.taxable_income <= previous_limit:
                break
            
            taxable_in_slab = min(self.taxable_income, slab_limit) - previous_limit
            tax += taxable_in_slab * rate
            previous_limit = slab_limit

        return tax

    def get_summary(self):
        """Return complete tax calculation"""
        tax = self.calculate_tax()
        cess = tax * 0.04
        total_tax = tax + cess

        return {
            "gross_income": self.annual_income,
            "taxable_income": self.taxable_income,
            "income_tax": round(tax, 2),
            "cess_4pct": round(cess, 2),
            "total_tax": round(total_tax, 2),
            "net_income": round(self.annual_income - total_tax, 2)
        }
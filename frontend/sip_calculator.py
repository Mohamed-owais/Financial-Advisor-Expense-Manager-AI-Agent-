class SIPCalculator:
    """Systematic Investment Plan Calculator"""
    
    def __init__(self, monthly_investment, annual_return_pct=12, years=10):
        self.monthly_investment = monthly_investment
        self.annual_return = annual_return_pct / 100
        self.monthly_return = self.annual_return / 12
        self.months = years * 12
    
    def calculate_future_value(self):
        """Calculate future value using SIP formula"""
        if self.monthly_return == 0:
            return self.monthly_investment * self.months
        
        # FV = PMT × [((1 + r)^n - 1) / r] × (1 + r)
        fv = self.monthly_investment * (
            ((1 + self.monthly_return) ** self.months - 1) / self.monthly_return
        ) * (1 + self.monthly_return)
        
        return fv
    
    def get_breakdown(self):
        """Get investment breakdown"""
        total_invested = self.monthly_investment * self.months
        future_value = self.calculate_future_value()
        gains = future_value - total_invested
        
        roi = (gains / total_invested) * 100 if total_invested > 0 else 0
        
        return {
            "total_invested": round(total_invested, 2),
            "future_value": round(future_value, 2),
            "gains": round(gains, 2),
            "roi_pct": round(roi, 2)
        }
    
    def get_year_by_year(self):
        """Get year-by-year projection"""
        results = []
        
        for year in range(1, (self.months // 12) + 1):
            months = year * 12
            invested = self.monthly_investment * months
            
            if self.monthly_return == 0:
                fv = invested
            else:
                fv = self.monthly_investment * (
                    ((1 + self.monthly_return) ** months - 1) / self.monthly_return
                ) * (1 + self.monthly_return)
            
            gains = fv - invested
            
            results.append({
                "year": year,
                "invested": round(invested, 2),
                "value": round(fv, 2),
                "gains": round(gains, 2)
            })
        
        return results
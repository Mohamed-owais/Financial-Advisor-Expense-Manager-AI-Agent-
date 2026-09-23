# Days 27-36: Core Features Only Plan

**Status:** After demo video, now adding Tax Calculator + SIP Calculator  
**Timeline:** 10 days  
**Hours available:** ~25 hours  
**Target:** Submission-ready with 2 new Indian features

---

## Days 27-28: Tax Calculator (2 days)

### Task 1: Create tax_calculator.py

```python
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
```

### Task 2: Add to streamlit_app.py

Add this section:

```python
# Tax Calculator Tab
if st.sidebar.button("💰 Tax Calculator"):
    st.header("Income Tax Calculator (FY 2024-25)")
    
    col1, col2 = st.columns(2)
    with col1:
        income = st.number_input("Annual Income (₹)", 100000, 10000000, 500000)
    with col2:
        st.info("Old Regime tax slabs")
    
    st.subheader("Apply Deductions")
    col1, col2 = st.columns(2)
    
    with col1:
        deduction_80c = st.number_input("80C - Investments (ELSS, PPF, LIC) (₹)", 0, 150000, 50000)
    with col2:
        deduction_80d = st.number_input("80D - Health Insurance (₹)", 0, 50000, 10000)
    
    # Calculate
    calc = IncomeTaxCalculator(income)
    calc.apply_deduction("80C", deduction_80c)
    calc.apply_deduction("80D", deduction_80d)
    
    summary = calc.get_summary()
    
    # Display results
    st.subheader("Tax Breakdown")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Gross Income", f"₹{summary['gross_income']:,.0f}")
    with col2:
        st.metric("Income Tax", f"₹{summary['income_tax']:,.0f}")
    with col3:
        st.metric("Cess (4%)", f"₹{summary['cess_4pct']:,.0f}")
    with col4:
        st.metric("Total Tax", f"₹{summary['total_tax']:,.0f}")
    
    st.success(f"**Net Income After Tax: ₹{summary['net_income']:,.0f}**")
    
    # Show taxable income
    st.info(f"Taxable Income: ₹{summary['taxable_income']:,.0f}")
```

### Checklist - Day 27-28
- [ ] Create tax_calculator.py
- [ ] Test with sample income (10L)
- [ ] Add to streamlit_app.py
- [ ] Test in browser
- [ ] Verify calculations
- [ ] No errors

---

## Days 29-30: SIP Calculator (2 days)

### Task 1: Create sip_calculator.py

```python
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
```

### Task 2: Add to streamlit_app.py

```python
# SIP Calculator Tab
if st.sidebar.button("📈 SIP Calculator"):
    st.header("SIP Investment Projections")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        monthly_inv = st.number_input("Monthly Investment (₹)", 1000, 100000, 5000, step=1000)
    with col2:
        ret_rate = st.slider("Expected Annual Return (%)", 6, 18, 12)
    with col3:
        years = st.slider("Time Horizon (Years)", 1, 30, 10)
    
    # Calculate
    calc = SIPCalculator(monthly_inv, ret_rate, years)
    breakdown = calc.get_breakdown()
    year_by_year = calc.get_year_by_year()
    
    # Summary
    st.subheader("Investment Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Monthly Investment", f"₹{monthly_inv:,.0f}")
    with col2:
        st.metric("Total Invested", f"₹{breakdown['total_invested']:,.0f}")
    with col3:
        st.metric("Gains", f"₹{breakdown['gains']:,.0f}")
    with col4:
        st.metric("Portfolio Value", f"₹{breakdown['future_value']:,.0f}")
    
    st.success(f"**ROI: {breakdown['roi_pct']:.1f}%**")
    
    # Year by year table
    st.subheader("Year-by-Year Projection")
    
    df = pd.DataFrame(year_by_year)
    st.dataframe(df, use_container_width=True)
    
    # Chart
    st.subheader("Growth Chart")
    fig, ax = plt.subplots(figsize=(10, 5))
    
    ax.plot(df['year'], df['invested'], label='Total Invested', marker='o')
    ax.plot(df['year'], df['value'], label='Portfolio Value', marker='s')
    ax.fill_between(df['year'], df['invested'], df['value'], alpha=0.2, label='Gains')
    
    ax.set_xlabel('Year')
    ax.set_ylabel('Amount (₹)')
    ax.set_title('SIP Growth Projection')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    st.pyplot(fig)
```

### Checklist - Day 29-30
- [ ] Create sip_calculator.py
- [ ] Test with 5K/month for 10 years
- [ ] Add to streamlit_app.py
- [ ] Test year-by-year table
- [ ] Test chart rendering
- [ ] No errors

---

## Days 31-32: Testing (2 days)

### Day 31: Tax Calculator Testing

Test cases:
- [ ] Income: ₹5,00,000 (no deductions)
- [ ] Income: ₹10,00,000 + 80C ₹1,50,000
- [ ] Income: ₹25,00,000 + all deductions
- [ ] Edge case: Income below 2.5L (should be 0 tax)

Expected outputs documented

### Day 32: SIP Calculator Testing

Test cases:
- [ ] 5K/month, 12% return, 10 years
- [ ] 10K/month, 15% return, 20 years
- [ ] 1K/month, 8% return, 30 years

Verify:
- [ ] Year-by-year values increase
- [ ] Gains calculation correct
- [ ] Chart displays properly
- [ ] No calculation errors

### Checklist - Days 31-32
- [ ] All tax calculations verified
- [ ] All SIP projections verified
- [ ] No bugs in Streamlit
- [ ] App runs without errors
- [ ] Both calculators working

---

## Days 33-36: Documentation & Polish (4 days)

### Day 33: Update README.md

Add:
- New features: Tax Calculator, SIP Calculator
- How to use each calculator
- Screenshots (if possible)
- Tax slab table
- SIP formula explanation

### Day 34: Code Cleanup

- Remove debug code
- Add comments
- Format with black
- Remove unused imports

### Day 35: Final Testing

- Complete end-to-end test
- All features working
- No errors in terminal
- Demo video still valid

### Day 36: Final Commit & Polish

- [ ] Update README with all features
- [ ] Add screenshots/descriptions
- [ ] Final git commit
- [ ] Push to GitHub
- [ ] Verify GitHub repo looks good

### Checklist - Days 33-36
- [ ] README updated
- [ ] Code clean and commented
- [ ] All features tested
- [ ] GitHub ready
- [ ] Submission-ready

---

## Final App Features (By Day 36)

**Streamlit Tabs:**
1. 📸 Upload Receipt
2. 📊 Dashboard
3. 💡 Financial Advice
4. 💰 Tax Calculator (NEW)
5. 📈 SIP Calculator (NEW)
6. 🧠 Advisor

**Features:**
- ✅ Receipt OCR extraction
- ✅ Expense tracking & dashboard
- ✅ AI financial advice
- ✅ Income tax calculation
- ✅ SIP projections
- ✅ Demo video recorded
- ✅ Full documentation

---

## Daily Checklist

| Day | Task | Hours | Status |
|-----|------|-------|--------|
| 27-28 | Tax Calculator | 4-5h | Planned |
| 29-30 | SIP Calculator | 4-5h | Planned |
| 31-32 | Testing | 4-5h | Planned |
| 33-36 | Docs + Polish | 4-5h | Planned |
| **Total** | | **16-20h** | On track |

---

## Success Criteria (By Day 36)

- ✅ Tax calculator: 10L income test case works
- ✅ SIP calculator: 10-year projection complete
- ✅ Both integrated in Streamlit
- ✅ No truncation, no errors
- ✅ Documentation complete
- ✅ GitHub ready for submission
- ✅ Demo video available

---

## What's NOT included (Skipped for time)

- ❌ PPF guide (can add later)
- ❌ UPI tracking (can add later)
- ❌ Data encryption (can add later)
- ❌ Security testing (can add later)
- ❌ Privacy compliance (can add later)

**Reason:** Time constraint. These can be added after submission if needed.

---

**Status:** ✅ Plan documented and ready to execute

**Next Step:** Start Day 27 - Create tax_calculator.py
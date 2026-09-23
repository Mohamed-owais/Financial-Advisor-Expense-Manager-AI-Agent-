import sys
sys.path.insert(0, r'C:\financial-advisor-ai')
import streamlit as st
from groq import Groq
import tempfile
import os
from backend.ocr.engine import extract_text_from_image
from backend.ai.analyzer import analyze_expense_with_groq
from backend.database.tracker import ExpenseTracker
from backend.config import GROQ_API_KEY, validate_config
import pandas as pd
import plotly.express as px
from tax_calculator import IncomeTaxCalculator

# Page config
st.set_page_config(page_title="Financial Advisor AI", layout="wide")

# Validate config on startup
try:
    validate_config()
except ValueError as e:
    st.error(f"Configuration Error: {e}")
    st.stop()

# Initialize Groq client
from groq import Groq as GroqClient
groq_client = GroqClient(api_key=GROQ_API_KEY)

# Initialize database
db = ExpenseTracker()

# Page title
st.title("💰 Financial Advisor AI")
st.subheader("AI-Powered Receipt & Expense Management")

# Create tabs - CORRECTED (added tab5 for Tax Calculator)
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📸 Upload Receipt", 
    "📊 View Expenses", 
    "💡 Financial Insights", 
    "🧠 Advisor",
    "💰 Tax Calculator"
])

# ==================== TAB 1: UPLOAD RECEIPT ====================
with tab1:
    st.write("### Upload a receipt image to extract expenses")
    
    uploaded_file = st.file_uploader("Choose a receipt image", type=["jpg", "jpeg", "png", "bmp"])
    
    if uploaded_file is not None:
        # Display uploaded image
        col1, col2 = st.columns(2)
        
        with col1:
            st.image(uploaded_file, caption="Uploaded Receipt", use_container_width=True)
        
        with col2:
            st.info("Processing receipt with AI OCR...\n\nThis may take 10-30 seconds on first run.")
        
        # Save image temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
            tmp_file.write(uploaded_file.getbuffer())
            temp_image_path = tmp_file.name
        
        try:
            # Step 1: Extract text with OCR
            st.write("**Step 1: Extracting text from image...**")
            extracted_text = extract_text_from_image(temp_image_path)
            st.success("✅ Text extracted!")
            
            with st.expander("📄 View Extracted Text"):
                st.text(extracted_text)
            
            # Step 2: Analyze with Groq
            st.write("**Step 2: Analyzing with AI...**")
            expense_data = analyze_expense_with_groq(extracted_text, groq_client)
            st.success("✅ Analysis complete!")
            
            # Step 3: Save to database
            st.write("**Step 3: Saving to database...**")
            if expense_data:
                db.add_expense({
                    "amount": float(expense_data.get('amount', 0)),
                    "vendor": expense_data.get('vendor', 'Unknown'),
                    "category": expense_data.get('category', 'Other'),
                    "date": expense_data.get('date', ''),
                    "items": [expense_data.get('item_name', 'Unknown')],
                    "currency": "INR",
                    "payment_method": "unknown",
                    "notes": ""
                })
                st.success("✅ Expense saved!")
                
                # Display parsed data
                st.write("### Extracted Expense Details:")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Amount", f"₹{expense_data.get('amount', 0)}")
                with col2:
                    st.metric("Category", expense_data.get('category', 'Other'))
                with col3:
                    st.metric("Vendor", expense_data.get('vendor', 'Unknown'))
                with col4:
                    st.metric("Date", expense_data.get('date', 'N/A'))
                
                # Raw JSON
                with st.expander("📋 View Raw JSON"):
                    st.json(expense_data)
            else:
                st.error("❌ Could not parse expense data")
        
        except Exception as e:
            st.error(f"❌ Error processing receipt: {str(e)}")
        
        finally:
            # Clean up temp file
            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)

# ==================== TAB 2: VIEW EXPENSES ====================
with tab2:
    st.write("### Your Expense History")
    
    expenses = db.get_all_expenses()
    
    if expenses.empty:
        st.info("No expenses recorded yet. Upload a receipt to get started!")
    else:
        # Display as table
        display_df = expenses[['id', 'amount', 'category', 'date', 'vendor']].copy()
        display_df.columns = ['ID', 'Amount (₹)', 'Category', 'Date', 'Vendor']
        st.dataframe(display_df, use_container_width=True)
        
        # Summary stats
        st.write("### Summary Statistics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total = expenses['amount'].sum()
            st.metric("Total Spent", f"₹{total:.2f}")
        
        with col2:
            st.metric("Number of Expenses", len(expenses))
        
        with col3:
            avg = expenses['amount'].mean()
            st.metric("Average Expense", f"₹{avg:.2f}")
        
        # Category breakdown
        st.write("### Expenses by Category")
        category_totals = {}
        for idx, row in expenses.iterrows():
            category = row['category']
            amount = row['amount']
            category_totals[category] = category_totals.get(category, 0) + amount
        
        if category_totals:
            fig = px.pie(
                names=list(category_totals.keys()),
                values=list(category_totals.values()),
                title="Expense Breakdown by Category"
            )
            st.plotly_chart(fig, use_container_width=True)

# ==================== TAB 3: FINANCIAL INSIGHTS ====================
with tab3:
    st.write("### 💡 Financial Insights & Recommendations")
    
    expenses = db.get_all_expenses()
    
    if expenses.empty:
        st.info("Add expenses first to get insights!")
    else:
        # Get insights from Groq
        expense_summary = f"Total expenses: {len(expenses)}\n"
        for idx, row in expenses.iterrows():
            expense_summary += f"- {row['vendor']}: ₹{row['amount']} ({row['category']})\n"
        
        try:
            insight_prompt = f"""Based on these expenses, provide brief financial advice (2-3 sentences):

{expense_summary}

Give actionable insights on spending patterns and savings tips."""

            message = groq_client.chat.completions.create(
                model="qwen/qwen3.8-27b",
                max_tokens=512,
                messages=[{"role": "user", "content": insight_prompt}]
            )
            
            insights = message.choices[0].message.content
            st.info(insights)
        
        except Exception as e:
            st.error(f"Error generating insights: {str(e)}")

# ==================== TAB 4: ADVISOR ====================
with tab4:
    st.write("### 🧠 Financial Advisor")
    
    expenses = db.get_all_expenses()
    
    if expenses.empty:
        st.info("Add expenses first to get personalized advice!")
    else:
        try:
            from backend.ai.financial_advisor import get_financial_advice, get_guru_comparison
            from backend.ai.gurus import WARREN_BUFFETT, ROBERT_KIYOSAKI, RAMIT_SETHI, INDIAN_CONTEXT
            
            # Calculate stats
            total_spent = expenses['amount'].sum()
            monthly_income = 50000  # Default, can be customized
            savings_goal = "Build emergency fund"
            
            # Get category breakdown
            category_totals = {}
            for idx, row in expenses.iterrows():
                category = row['category']
                amount = row['amount']
                category_totals[category] = category_totals.get(category, 0) + amount
            
            # Get AI advice
            user_profile = {
                "monthly_income": monthly_income,
                "top_expenses": category_totals,
                "monthly_budget": total_spent,
                "savings_goal": savings_goal
            }
            
            advice = get_financial_advice(user_profile)
            st.success("✅ AI Financial Advisor")
            st.info(advice)
            
            # Guru comparison
            st.write("### 📚 Guru Comparison")
            guru_select = st.selectbox("Choose a financial guru:", 
                                      ["Warren Buffett", "Robert Kiyosaki", "Ramit Sethi", "Indian Context"])
            
            if guru_select:
                guru_advice = get_guru_comparison(category_totals, guru_select)
                st.write(f"### {guru_select}'s Take:")
                st.info(guru_advice)
        
        except Exception as e:
            st.error(f"Error generating advice: {str(e)}")

# ==================== TAB 5: TAX CALCULATOR ====================
with tab5:
    st.header("Income Tax Calculator (FY 2024-25)")
    st.write("Calculate your annual income tax with deductions")
    
    col1, col2 = st.columns(2)
    with col1:
        income = st.number_input("Annual Income (₹)", 100000, 10000000, 500000)
    with col2:
        st.info("Old Regime Tax Slabs")
    
    st.subheader("Apply Tax Deductions")
    col1, col2 = st.columns(2)
    
    with col1:
        ded_80c = st.number_input("80C - Investments (ELSS, PPF, LIC) (₹)", 0, 150000, 50000)
    with col2:
        ded_80d = st.number_input("80D - Health Insurance (₹)", 0, 50000, 10000)
    
    col1, col2 = st.columns(2)
    with col1:
        ded_80e = st.number_input("80E - Education Loan Interest (₹)", 0, 50000, 0)
    with col2:
        ded_80ccd = st.number_input("80CCD - NPS (₹)", 0, 50000, 0)
    
    # Calculate tax
    calc = IncomeTaxCalculator(income)
    calc.apply_deduction("80C", ded_80c)
    calc.apply_deduction("80D", ded_80d)
    calc.apply_deduction("80E", ded_80e)
    calc.apply_deduction("80CCD", ded_80ccd)
    
    summary = calc.get_summary()
    
    # Display results
    st.subheader("Tax Calculation Breakdown")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Gross Income", f"₹{summary['gross_income']:,.0f}")
    with col2:
        st.metric("Taxable Income", f"₹{summary['taxable_income']:,.0f}")
    with col3:
        st.metric("Income Tax", f"₹{summary['income_tax']:,.0f}")
    with col4:
        st.metric("Cess (4%)", f"₹{summary['cess_4pct']:,.0f}")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        st.error(f"**Total Tax: ₹{summary['total_tax']:,.0f}**")
    with col2:
        st.success(f"**Net Income: ₹{summary['net_income']:,.0f}**")
    
    # Tax slab info
    st.info("""
    **Tax Slabs (Old Regime FY 2024-25):**
    - ₹0 - ₹2,50,000: 0%
    - ₹2,50,000 - ₹5,00,000: 5%
    - ₹5,00,000 - ₹10,00,000: 20%
    - Above ₹10,00,000: 30%
    - Plus 4% cess on total tax
    """)

# Footer
st.divider()
st.caption("Financial Advisor AI - Powered by EasyOCR & Groq LLM")
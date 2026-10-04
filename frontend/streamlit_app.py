# System imports
import sys
import os
import time
import tempfile

# Data & Database
import pandas as pd
import sqlite3

# UI & Visualization
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# AI & Encryption
from groq import Groq
from encryption import DatabaseEncryption

# Local modules
sys.path.insert(0, r'C:\financial-advisor-ai')
from backend.ocr.engine import extract_text_from_image
from backend.ai.analyzer import analyze_expense_with_groq
from backend.database.tracker import ExpenseTracker
from backend.config import GROQ_API_KEY, validate_config
from tax_calculator import IncomeTaxCalculator
from sip_calculator import SIPCalculator

"""
Financial Advisor AI - Receipt OCR & Expense Management

Features:
- Upload receipts → Extract expenses with AI OCR
- View expenses with charts and analytics  
- Get personalized financial advice from AI & gurus
- Calculate income taxes (FY 2024-25)
- Project SIP investment returns
- Encrypted database for privacy
"""

# ============ CUSTOM STYLING ============
st.markdown("""
<style>
/* Root colors - Dark theme ONLY */
:root {
    --color-navy: #0F172A;
    --color-slate: #1E293B;
    --color-slate-light: #334155;
    --color-emerald: #10B981;
    --color-emerald-dark: #059669;
    --color-indigo: #6366F1;
    --color-coral: #FF6B6B;
    --color-text-primary: #FFFFFF;
    --color-text-secondary: #CBD5E1;
    --color-text-muted: #94A3B8;
    --color-border: #475569;
    color-scheme: dark !important;
}

* {
    font-family: 'Inter', 'Segoe UI', sans-serif;
    color-scheme: dark !important;
}

/* GLOBAL DARK THEME - OVERRIDE EVERYTHING */
html {
    color-scheme: dark !important;
    background: var(--color-navy) !important;
}

body {
    background: var(--color-navy) !important;
    color: var(--color-text-primary) !important;
}

[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0A0F1B 0%, #0F1419 50%, #0A0F1B 100%) !important;
}

[data-testid="stSidebar"] {
    background: var(--color-slate) !important;
    border-right: 2px solid var(--color-indigo) !important;
}

[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0A0F1B 0%, #0F1419 50%, #0A0F1B 100%) !important;
}

[data-testid="stSidebar"] {
    background: var(--color-slate) !important;
    border-right: 2px solid var(--color-indigo) !important;
}

/* Hero header - Bold gradient */
.hero-header {
    background: linear-gradient(135deg, var(--color-navy) 0%, var(--color-slate) 50%, #1a254d 100%);
    color: var(--color-text-primary);
    padding: 3rem 2rem;
    border-radius: 16px;
    margin-bottom: 2.5rem;
    text-align: center;
    box-shadow: 0 8px 32px rgba(16, 185, 129, 0.15);
    border-top: 3px solid var(--color-emerald);
    border-bottom: 2px solid var(--color-indigo);
    position: relative;
    overflow: hidden;
}

.hero-header::before {
    content: '';
    position: absolute;
    top: 0;
    right: -50%;
    width: 100%;
    height: 100%;
    background: radial-gradient(circle, rgba(99, 102, 241, 0.1) 0%, transparent 70%);
    pointer-events: none;
}

.hero-header h1 {
    margin: 0 0 0.5rem 0;
    font-size: 2.75rem;
    font-weight: 700;
    color: var(--color-text-primary);
    position: relative;
    z-index: 1;
}

.hero-header p {
    margin: 0;
    font-size: 1.15rem;
    opacity: 0.9;
    color: var(--color-text-secondary);
    position: relative;
    z-index: 1;
}

/* Section headers - Bold with accent */
.section-header {
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--color-text-primary);
    margin: 2.5rem 0 1.5rem 0;
    padding-bottom: 1rem;
    border-bottom: 2px solid var(--color-border);
    position: relative;
}

.section-header::after {
    content: '';
    position: absolute;
    left: 0;
    bottom: -2px;
    height: 2px;
    width: 80px;
    background: linear-gradient(90deg, var(--color-emerald), var(--color-indigo));
}

/* Tabs - Dark with emerald accent */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem;
    border-bottom: 2px solid var(--color-border);
    padding-bottom: 0;
}

.stTabs [data-baseweb="tab-list"] button {
    color: var(--color-text-muted) !important;
    border-bottom: 3px solid transparent !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    background: transparent !important;
    padding: 0.75rem 1.25rem !important;
    transition: all 0.3s ease !important;
}

.stTabs [data-baseweb="tab-list"] button:hover {
    color: var(--color-emerald) !important;
}

.stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
    color: var(--color-emerald) !important;
    border-bottom-color: var(--color-emerald) !important;
    background: rgba(16, 185, 129, 0.1) !important;
}

/* Metrics - Dark slate with colored left border */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, var(--color-slate) 0%, rgba(51, 65, 85, 0.5) 100%) !important;
    border: 1px solid var(--color-border) !important;
    border-left: 4px solid var(--color-emerald) !important;
    border-radius: 12px !important;
    padding: 1.5rem !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3) !important;
    transition: all 0.3s ease !important;
}

[data-testid="metric-container"]:hover {
    box-shadow: 0 8px 24px rgba(16, 185, 129, 0.2) !important;
    border-left-color: var(--color-coral) !important;
    transform: translateY(-2px) !important;
}

[data-testid="metric-container"] > div > div > div {
    color: var(--color-text-primary) !important;
}

/* Divider - Gradient */
hr {
    border: none !important;
    height: 2px !important;
    background: linear-gradient(90deg, transparent, var(--color-indigo), transparent) !important;
    margin: 2rem 0 !important;
}

/* Info/Success/Warning boxes - Dark with colored left border */
.stAlert {
    border-radius: 12px !important;
    border-left: 4px solid var(--color-emerald) !important;
    background: linear-gradient(90deg, rgba(16, 185, 129, 0.1) 0%, transparent 100%) !important;
    border: 1px solid var(--color-border) !important;
    padding: 1.25rem !important;
}

.stAlert > div {
    color: var(--color-text-secondary) !important;
}

/* Buttons - Emerald with glow */
.stButton > button {
    background: var(--color-emerald) !important;
    color: var(--color-navy) !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    padding: 0.8rem 1.75rem !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3) !important;
}

.stButton > button:hover {
    background: var(--color-emerald-dark) !important;
    box-shadow: 0 8px 24px rgba(16, 185, 129, 0.5) !important;
    transform: translateY(-2px) !important;
}

/* INPUT FIELDS - FORCE DARK EVERYWHERE */
input, select, textarea {
    background: var(--color-slate-light) !important;
    color: var(--color-text-primary) !important;
    border: 2px solid var(--color-emerald) !important;
    border-radius: 10px !important;
    caret-color: var(--color-emerald) !important;
}

.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div > select,
.stDateInput > div > div > input {
    border: 2px solid var(--color-emerald) !important;
    border-radius: 10px !important;
    font-size: 1rem !important;
    background: var(--color-slate-light) !important;
    color: var(--color-text-primary) !important;
    padding: 0.85rem 1.1rem !important;
    font-weight: 500 !important;
}

.stDateInput > div > div > input::-webkit-calendar-picker-indicator {
    filter: invert(0.8);
}

.stTextInput > div > div > input::placeholder,
.stNumberInput > div > div > input::placeholder {
    color: var(--color-text-muted) !important;
}

.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stSelectbox > div > div > select:focus,
.stDateInput > div > div > input:focus {
    border-color: var(--color-indigo) !important;
    box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.3), 0 0 0 8px rgba(16, 185, 129, 0.1) !important;
    outline: none !important;
}

/* NUMBER INPUT +/- BUTTONS - EMERALD */
.stNumberInput button {
    background: var(--color-emerald) !important;
    color: var(--color-navy) !important;
    border: none !important;
    font-weight: 700 !important;
    font-size: 18px !important;
    transition: all 0.2s ease !important;
}

.stNumberInput button:hover {
    background: var(--color-emerald-dark) !important;
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4) !important;
}

/* SELECTBOX - Custom Dark Styling */
.stSelectbox {
    width: 100%;
}

.stSelectbox > div {
    width: 100%;
}

.stSelectbox > div > div {
    width: 100%;
}

select {
    background: var(--color-slate-light) !important;
    color: var(--color-text-primary) !important;
    border: 2px solid var(--color-emerald) !important;
    border-radius: 10px !important;
    padding: 0.75rem 1rem !important;
    font-size: 1rem !important;
    font-weight: 500 !important;
    cursor: pointer !important;
    appearance: none !important;
    -webkit-appearance: none !important;
    -moz-appearance: none !important;
    background-image: url("data:image/svg+xml;charset=UTF-8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2310B981' stroke-width='2'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E") !important;
    background-repeat: no-repeat !important;
    background-position: right 0.75rem center !important;
    background-size: 1.25em 1.25em !important;
    padding-right: 2.5rem !important;
}

/* Option styling - Force dark in dropdown */
option {
    background: var(--color-slate-light) !important;
    color: var(--color-text-primary) !important;
}

option:checked {
    background: var(--color-emerald) !important;
    color: var(--color-navy) !important;
}

option:hover {
    background: var(--color-emerald) !important;
    color: var(--color-navy) !important;
}

/* Webkit scrollbar for dropdown */
select::-webkit-scrollbar {
    width: 10px;
}

select::-webkit-scrollbar-track {
    background: var(--color-slate-light) !important;
}

select::-webkit-scrollbar-thumb {
    background: var(--color-emerald) !important;
    border-radius: 5px;
}

select::-webkit-scrollbar-thumb:hover {
    background: var(--color-emerald-dark) !important;
}

/* File uploader - FORCE DARK EVERYWHERE */
[data-testid="fileUploadDropzone"] {
    background: var(--color-slate-light) !important;
    border: 2px dashed var(--color-indigo) !important;
    border-radius: 12px !important;
    padding: 2rem !important;
}

[data-testid="fileUploadDropzone"] > div {
    background: var(--color-slate-light) !important;
    color: var(--color-text-primary) !important;
}

[data-testid="fileUploadDropzone"] > div > div {
    background: var(--color-slate-light) !important;
    color: var(--color-text-primary) !important;
}

[data-testid="fileUploadDropzone"] > div > div > div {
    background: var(--color-slate-light) !important;
    color: var(--color-text-primary) !important;
}

[data-testid="fileUploadDropzone"] button {
    background: var(--color-emerald) !important;
    color: var(--color-navy) !important;
    border: none !important;
    font-weight: 600 !important;
}

[data-testid="fileUploadDropzone"] span {
    color: var(--color-text-primary) !important;
}

/* All file uploader text dark */
.stFileUploader {
    background: var(--color-navy) !important;
}

.stFileUploader * {
    background: var(--color-slate-light) !important;
    color: var(--color-text-primary) !important;
}

/* Dataframe */
.stDataFrame {
    border-radius: 12px !important;
    border: 1px solid var(--color-border) !important;
    background: var(--color-slate) !important;
}

/* Plotly charts */
.plotly-graph-div {
    border-radius: 12px !important;
    background: var(--color-slate) !important;
    border: 1px solid var(--color-border) !important;
}

/* Expander */
.streamlit-expanderHeader {
    font-weight: 600 !important;
    color: var(--color-text-primary) !important;
    border-left: 3px solid var(--color-coral) !important;
    padding-left: 1rem !important;
    background: rgba(51, 65, 85, 0.5) !important;
    border-radius: 8px !important;
}

/* Footer */
.footer {
    text-align: right;
    color: var(--color-text-muted);
    font-size: 0.9rem;
    margin-top: 3rem;
    padding-top: 1.5rem;
    border-top: 2px solid var(--color-border);
    opacity: 0.8;
}

/* Generic text */
p, div, span, label {
    color: var(--color-text-primary) !important;
}

/* Labels - Bold */
label {
    font-weight: 600 !important;
    color: var(--color-text-secondary) !important;
    margin-bottom: 0.75rem !important;
}

/* Write text */
[data-testid="stMarkdownContainer"] {
    color: var(--color-text-secondary) !important;
}
</style>
""", unsafe_allow_html=True)

# ============ CACHED FUNCTIONS ============
@st.cache_data(ttl=3600)
def get_insights_cached(expense_summary):
    """Cache insights to avoid rate limiting"""
    time.sleep(2)
    
    insight_prompt = f"""Based on these expenses, provide brief financial advice (2-3 sentences):

{expense_summary}

Give actionable insights on spending patterns and savings tips."""

    message = groq_client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        max_tokens=512,
        messages=[{"role": "user", "content": insight_prompt}]
    )
    
    return message.choices[0].message.content

@st.cache_data(ttl=3600)
def get_guru_comparison_cached(category_totals, guru_select):
    """Cache guru comparison to avoid repeated LLM calls"""
    time.sleep(1)
    return get_guru_comparison(category_totals, guru_select)

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

# Hero Header
st.markdown("""
<div class="hero-header">
    <h1>💰 Financial Advisor AI</h1>
    <p>AI-Powered Receipt & Expense Management</p>
</div>
""", unsafe_allow_html=True)

# Create tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📸 Upload Receipt", 
    "📊 View Expenses", 
    "💡 Financial Insights", 
    "🧠 Advisor",
    "💰 Tax Calculator",
    "📈 SIP Calculator"
])

# ==================== TAB 1: UPLOAD RECEIPT ====================
with tab1:
    st.markdown('<div class="section-header">Upload Receipt</div>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Choose a receipt image", type=["jpg", "jpeg", "png", "bmp"])
    
    if uploaded_file is not None:
        col1, col2 = st.columns([1.5, 1], gap="large")
        
        with col1:
            st.image(uploaded_file, caption="Receipt Preview", use_container_width=True)
        
        with col2:
            st.info("Processing receipt with AI OCR...\n\nThis may take 10-30 seconds on first run.")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
            tmp_file.write(uploaded_file.getbuffer())
            temp_image_path = tmp_file.name
        
        try:
            st.write("**Step 1: Extracting text from image...**")
            extracted_text = extract_text_from_image(temp_image_path)
            st.success("✅ Text extracted!")
            
            with st.expander("📄 View Extracted Text"):
                st.text(extracted_text)
            
            st.write("**Step 2: Analyzing with AI...**")
            expense_data = analyze_expense_with_groq(extracted_text, groq_client)
            st.success("✅ Analysis complete!")
            
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
                
                st.markdown('<div class="section-header">Extracted Expense Details</div>', unsafe_allow_html=True)
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Amount", f"₹{expense_data.get('amount', 0)}")
                with col2:
                    st.metric("Category", expense_data.get('category', 'Other'))
                with col3:
                    st.metric("Vendor", expense_data.get('vendor', 'Unknown'))
                with col4:
                    st.metric("Date", expense_data.get('date', 'N/A'))
                
                with st.expander("📋 View Raw JSON"):
                    st.json(expense_data)
            else:
                st.error("❌ Could not parse expense data")
        
        except Exception as e:
            st.error(f"❌ Error processing receipt: {str(e)}")
        
        finally:
            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)
    
    st.divider()
    st.markdown('<div class="section-header">Manual Entry</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Store/Vendor Name**")
        manual_store = st.text_input("", placeholder="Enter store name", key="store_name")
        st.markdown("**Amount (₹)**")
        manual_amount = st.number_input("", min_value=0.0, step=10.0, value=0.0, key="amount")
    
    with col2:
        st.markdown("**Category**")
        categories = ["Food", "Groceries", "Transport", "Shopping", "Entertainment", "Utilities", "Other"]
        # Use selectbox but add custom styling
        manual_category = st.selectbox("", categories, key="category")
        st.markdown("**Date**")
        manual_date = st.date_input("", key="date")
    
    if st.button("➕ Add Manual Entry"):
        if not manual_store or manual_store.strip() == "":
            st.warning("⚠️ Enter a store name")
        elif manual_amount <= 0:
            st.warning("⚠️ Amount must be > 0")
        elif not manual_category:
            st.warning("⚠️ Select a category")
        else:
            try:
                db.add_expense({
                    "amount": manual_amount,
                    "vendor": manual_store.strip(),
                    "category": manual_category,
                    "date": str(manual_date),
                    "items": [manual_store],
                    "currency": "INR",
                    "payment_method": "manual",
                    "notes": "Manual entry"
                })
                st.success(f"✅ Added: {manual_store} - ₹{manual_amount}")
            except Exception as e:
                st.error(f"❌ Database error: {str(e)}")

# ==================== TAB 2: VIEW EXPENSES ====================
with tab2:
    st.markdown('<div class="section-header">Your Expense History</div>', unsafe_allow_html=True)
    
    expenses = db.get_all_expenses()
    
    if expenses.empty:
        st.info("No expenses recorded yet. Upload a receipt to get started!")
    else:
        display_df = expenses[['id', 'amount', 'category', 'date', 'vendor']].copy()
        display_df.columns = ['ID', 'Amount (₹)', 'Category', 'Date', 'Vendor']
        st.dataframe(display_df, use_container_width=True)
        
        st.markdown('<div class="section-header">Summary Statistics</div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total = expenses['amount'].sum()
            st.metric("Total Spent", f"₹{total:.2f}")
        
        with col2:
            count = len(expenses)
            st.metric("Total Expenses", count)
        
        with col3:
            avg = expenses['amount'].mean()
            st.metric("Average Expense", f"₹{avg:.2f}")
        
        st.markdown('<div class="section-header">Expenses by Category</div>', unsafe_allow_html=True)
        category_totals = {}
        for idx, row in expenses.iterrows():
            category = row['category']
            amount = row['amount']
            category_totals[category] = category_totals.get(category, 0) + amount
        
        if category_totals:
            fig = px.bar(
                x=list(category_totals.keys()),
                y=list(category_totals.values()),
                title="Spending by Category",
                labels={'x': 'Category', 'y': 'Amount (₹)'},
                color_discrete_sequence=['#10B981']
            )
            fig.update_layout(
                plot_bgcolor='rgba(30, 41, 59, 0.5)',
                paper_bgcolor='rgba(15, 23, 42, 0)',
                font=dict(family="Inter, sans-serif", size=12, color="#CBD5E1"),
                margin=dict(l=0, r=0, t=30, b=0),
                height=400,
                showlegend=False
            )
            fig.update_xaxes(showgrid=False, color="#CBD5E1")
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(71, 85, 105, 0.3)', color="#CBD5E1")
            st.plotly_chart(fig, use_container_width=True)

# ==================== TAB 3: FINANCIAL INSIGHTS ====================
with tab3:
    st.markdown('<div class="section-header">Financial Insights & Recommendations</div>', unsafe_allow_html=True)
    
    expenses = db.get_all_expenses()
    
    if expenses.empty:
        st.info("Add expenses first to get insights!")
    else:
        expense_summary = f"Total expenses: {len(expenses)}\n"
        for idx, row in expenses.iterrows():
            expense_summary += f"- {row['vendor']}: ₹{row['amount']} ({row['category']})\n"
        
        try:
            insights = get_insights_cached(expense_summary)
            st.info(insights)
        except Exception as e:
            st.error(f"Error generating insights: {str(e)}")

# ==================== TAB 4: ADVISOR ====================
with tab4:
    st.markdown('<div class="section-header">Financial Advisor</div>', unsafe_allow_html=True)
    
    expenses = db.get_all_expenses()
    
    if expenses.empty:
        st.info("Add expenses first to get personalized advice!")
    else:
        try:
            from backend.ai.financial_advisor import get_financial_advice, get_guru_comparison
            from backend.ai.gurus import WARREN_BUFFETT, ROBERT_KIYOSAKI, RAMIT_SETHI, INDIAN_CONTEXT
            
            total_spent = expenses['amount'].sum()
            monthly_income = 50000
            savings_goal = "Build emergency fund"
            
            category_totals = {}
            for idx, row in expenses.iterrows():
                category = row['category']
                amount = row['amount']
                category_totals[category] = category_totals.get(category, 0) + amount
            
            user_profile = {
                "monthly_income": monthly_income,
                "top_expenses": category_totals,
                "monthly_budget": total_spent,
                "savings_goal": savings_goal
            }
            
            advice = get_financial_advice(user_profile)
            st.success("✅ AI Financial Advisor")
            st.info(advice)
            
            st.markdown('<div class="section-header">Guru Comparison</div>', unsafe_allow_html=True)
            guru_select = st.selectbox("Choose a financial guru:", 
                                      ["Warren Buffett", "Robert Kiyosaki", "Ramit Sethi", "Indian Context"])
            
            if guru_select:
                expenses_tuple = tuple(sorted(category_totals.items()))
                guru_advice = get_guru_comparison_cached(expenses_tuple, guru_select)
                st.write(f"### {guru_select}'s Take:")
                st.info(guru_advice)
        
        except Exception as e:
            st.error(f"Error generating advice: {str(e)}")

# ==================== TAB 5: TAX CALCULATOR ====================
with tab5:
    st.markdown('<div class="section-header">Income Tax Calculator (FY 2024-25)</div>', unsafe_allow_html=True)
    st.write("Calculate your annual income tax with deductions")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Annual Income (₹)**")
        income = st.number_input("", 100000, 10000000, 500000, key="income")
    with col2:
        st.info("Old Regime Tax Slabs")
    
    st.markdown('<div class="section-header">Apply Tax Deductions</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**80C - Investments (ELSS, PPF, LIC) (₹)**")
        ded_80c = st.number_input("", 0, 150000, 50000, key="80c")
    with col2:
        st.markdown("**80D - Health Insurance (₹)**")
        ded_80d = st.number_input("", 0, 50000, 10000, key="80d")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**80E - Education Loan Interest (₹)**")
        ded_80e = st.number_input("", 0, 50000, 0, key="80e")
    with col2:
        st.markdown("**80CCD - NPS (₹)**")
        ded_80ccd = st.number_input("", 0, 50000, 0, key="80ccd")
    
    if income < 0:
        st.error("❌ Income cannot be negative")
    elif ded_80c < 0 or ded_80d < 0 or ded_80e < 0 or ded_80ccd < 0:
        st.error("❌ Deductions cannot be negative")
    else:
        calc = IncomeTaxCalculator(income)
        calc.apply_deduction("80C", ded_80c)
        calc.apply_deduction("80D", ded_80d)
        calc.apply_deduction("80E", ded_80e)
        calc.apply_deduction("80CCD", ded_80ccd)
        
        summary = calc.get_summary()
        
        st.markdown('<div class="section-header">Tax Calculation Breakdown</div>', unsafe_allow_html=True)
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
        
        st.info("""
        **Tax Slabs (Old Regime FY 2024-25):**
        - ₹0 - ₹2,50,000: 0%
        - ₹2,50,000 - ₹5,00,000: 5%
        - ₹5,00,000 - ₹10,00,000: 20%
        - Above ₹10,00,000: 30%
        - Plus 4% cess on total tax
        """)

# ==================== TAB 6: SIP CALCULATOR ====================
with tab6:
    st.markdown('<div class="section-header">SIP Investment Projections</div>', unsafe_allow_html=True)
    st.write("Calculate your Systematic Investment Plan returns")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Monthly Investment (₹)**")
        monthly_inv = st.number_input("", 1000, 100000, 5000, step=1000, key="monthly_inv")
    with col2:
        st.markdown("**Expected Annual Return (%)**")
        ret_rate = st.slider("", 6, 18, 12, key="ret_rate")
    with col3:
        st.markdown("**Time Horizon (Years)**")
        years = st.slider("", 1, 30, 10, key="years")
    
    if monthly_inv <= 0:
        st.error("❌ Monthly investment must be > 0")
    elif years <= 0:
        st.error("❌ Years must be > 0")
    elif ret_rate < 0 or ret_rate > 30:
        st.error("❌ Return rate should be 0-30%")
    else:
        calc = SIPCalculator(monthly_inv, ret_rate, years)
        breakdown = calc.get_breakdown()
        year_by_year = calc.get_year_by_year()
        
        st.markdown('<div class="section-header">Investment Summary</div>', unsafe_allow_html=True)
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
        
        st.markdown('<div class="section-header">Year-by-Year Projection</div>', unsafe_allow_html=True)
        df = pd.DataFrame(year_by_year)
        st.dataframe(df, use_container_width=True)
        
        st.markdown('<div class="section-header">Growth Chart</div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['year'], y=df['invested'],
            name='Invested',
            fill='tozeroy',
            line=dict(color='#FF6B6B', width=2)
        ))
        fig.add_trace(go.Scatter(
            x=df['year'], y=df['value'],
            name='Portfolio Value',
            fill='tonexty',
            line=dict(color='#10B981', width=2)
        ))
        fig.update_layout(
            title='SIP Growth Projection',
            xaxis_title='Year',
            yaxis_title='Amount (₹)',
            plot_bgcolor='rgba(30, 41, 59, 0.5)',
            paper_bgcolor='rgba(15, 23, 42, 0)',
            font=dict(family="Inter, sans-serif", size=12, color="#CBD5E1"),
            height=400,
            hovermode='x unified'
        )
        fig.update_xaxes(showgrid=False, color="#CBD5E1")
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(71, 85, 105, 0.3)', color="#CBD5E1")
        st.plotly_chart(fig, use_container_width=True)

st.markdown("""
<div class="footer">
Financial Advisor AI — Powered by EasyOCR & Groq LLM
</div>
""", unsafe_allow_html=True)
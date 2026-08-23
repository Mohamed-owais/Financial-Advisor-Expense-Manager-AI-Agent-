"""
Financial Advisor MVP - Streamlit Web App
Complete expense management and AI-powered financial insights dashboard
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from ocr_engine import OCREngine
from expense_tracker import ExpenseTracker
import json

# Page configuration
st.set_page_config(
    page_title="Financial Advisor AI",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 12px;
        border-radius: 5px;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 12px;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "ocr_engine" not in st.session_state:
    st.session_state.ocr_engine = OCREngine()

if "expense_tracker" not in st.session_state:
    st.session_state.expense_tracker = ExpenseTracker()

# App title
st.title("💰 Financial Advisor AI")
st.markdown("*Intelligent expense tracking powered by OCR and AI*")

# Sidebar navigation
with st.sidebar:
    st.header("Navigation")
    page = st.radio(
        "Select a page:",
        ["📊 Dashboard", "📸 Add Expense", "📈 Analytics", "⚙️ Settings"]
    )
    
    st.markdown("---")
    st.markdown("### About")
    st.info("Upload receipt images, extract expenses with AI, and track spending patterns.")

# PAGE 1: DASHBOARD
if page == "📊 Dashboard":
    st.header("Dashboard")
    
    # Get all expenses
    expenses_df = st.session_state.expense_tracker.get_all_expenses()
    
    if not expenses_df.empty:
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_spent = expenses_df['amount'].sum()
            st.metric("Total Spent", f"₹{total_spent:.2f}")
        
        with col2:
            avg_expense = expenses_df['amount'].mean()
            st.metric("Average Expense", f"₹{avg_expense:.2f}")
        
        with col3:
            num_expenses = len(expenses_df)
            st.metric("Total Transactions", num_expenses)
        
        with col4:
            unique_vendors = expenses_df['vendor'].nunique()
            st.metric("Vendors", unique_vendors)
        
        # Expense distribution by category
        st.subheader("Expense Distribution by Category")
        category_summary = expenses_df.groupby('category')['amount'].sum().sort_values(ascending=False)
        
        fig_pie = px.pie(
            values=category_summary.values,
            names=category_summary.index,
            title="Spending by Category"
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Recent expenses table
        st.subheader("Recent Expenses")
        display_df = expenses_df[['id', 'vendor', 'amount', 'currency', 'category', 'date']].copy()
        display_df = display_df.sort_values('date', ascending=False).head(10)
        st.dataframe(display_df, use_container_width=True)
    else:
        st.info("No expenses recorded yet. Start by adding an expense!")

# PAGE 2: ADD EXPENSE
elif page == "📸 Add Expense":
    st.header("Add New Expense")
    
    # Two columns for manual entry and OCR
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📸 OCR Receipt Upload")
        
        uploaded_file = st.file_uploader(
            "Upload a receipt or payment screenshot",
            type=["jpg", "jpeg", "png", "bmp", "gif"]
        )
        
        if uploaded_file is not None:
            st.info("Processing your receipt...")
            
            # Display uploaded image
            st.image(uploaded_file, use_container_width=True)
            
            # Process with OCR
            with st.spinner("Extracting text from receipt..."):
                image_bytes = uploaded_file.read()
                ocr_result = st.session_state.ocr_engine.process_from_bytes(image_bytes)
            
            if ocr_result.get("success"):
                st.success("✅ Receipt processed successfully!")
                
                # Display extracted expense data
                st.subheader("Extracted Expense Details")
                
                # Create form to review/edit extracted data
                col_a, col_b = st.columns(2)
                
                with col_a:
                    amount = st.number_input(
                        "Amount",
                        value=float(ocr_result.get("amount", 0)),
                        min_value=0.0
                    )
                    currency = st.selectbox(
                        "Currency",
                        ["INR", "USD", "EUR", "GBP"],
                        index=0 if ocr_result.get("currency") == "INR" else 0
                    )
                    vendor = st.text_input(
                        "Vendor/Store",
                        value=ocr_result.get("vendor", "")
                    )
                
                with col_b:
                    category = st.selectbox(
                        "Category",
                        [
                            "Food & Dining",
                            "Transportation",
                            "Entertainment",
                            "Shopping",
                            "Bills & Utilities",
                            "Healthcare",
                            "Education",
                            "Travel",
                            "Groceries",
                            "Other"
                        ],
                        index=0 if ocr_result.get("category") == "Food & Dining" else 0
                    )
                    date = st.date_input(
                        "Date",
                        value=datetime.now()
                    )
                    payment_method = st.selectbox(
                        "Payment Method",
                        ["card", "cash", "upi", "online", "unknown"]
                    )
                
                items = st.text_area(
                    "Items purchased (comma-separated)",
                    value=", ".join(ocr_result.get("items", []))
                )
                
                notes = st.text_area(
                    "Additional notes",
                    value=ocr_result.get("notes", "")
                )
                
                # Save expense button
                if st.button("💾 Save Expense", type="primary"):
                    expense_data = {
                        "amount": amount,
                        "currency": currency,
                        "vendor": vendor,
                        "category": category,
                        "items": [item.strip() for item in items.split(",")],
                        "date": date.strftime("%Y-%m-%d"),
                        "payment_method": payment_method,
                        "notes": notes
                    }
                    
                    try:
                        expense_id = st.session_state.expense_tracker.add_expense(expense_data)
                        st.success(f"✅ Expense saved successfully! (ID: {expense_id})")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error saving expense: {str(e)}")
            else:
                st.error(f"❌ Failed to process receipt: {ocr_result.get('error', 'Unknown error')}")
    
    with col2:
        st.subheader("📝 Manual Entry")
        
        manual_amount = st.number_input(
            "Amount",
            min_value=0.0,
            step=10.0,
            key="manual_amount"
        )
        
        manual_currency = st.selectbox(
            "Currency",
            ["INR", "USD", "EUR", "GBP"],
            key="manual_currency"
        )
        
        manual_vendor = st.text_input(
            "Vendor/Store",
            key="manual_vendor"
        )
        
        manual_category = st.selectbox(
            "Category",
            [
                "Food & Dining",
                "Transportation",
                "Entertainment",
                "Shopping",
                "Bills & Utilities",
                "Healthcare",
                "Education",
                "Travel",
                "Groceries",
                "Other"
            ],
            key="manual_category"
        )
        
        manual_date = st.date_input(
            "Date",
            value=datetime.now(),
            key="manual_date"
        )
        
        manual_payment = st.selectbox(
            "Payment Method",
            ["card", "cash", "upi", "online", "unknown"],
            key="manual_payment"
        )
        
        manual_items = st.text_area(
            "Items (comma-separated)",
            key="manual_items"
        )
        
        manual_notes = st.text_area(
            "Notes",
            key="manual_notes"
        )
        
        if st.button("💾 Save Manual Entry", type="primary", key="save_manual"):
            if manual_amount > 0 and manual_vendor:
                expense_data = {
                    "amount": manual_amount,
                    "currency": manual_currency,
                    "vendor": manual_vendor,
                    "category": manual_category,
                    "items": [item.strip() for item in manual_items.split(",")] if manual_items else [],
                    "date": manual_date.strftime("%Y-%m-%d"),
                    "payment_method": manual_payment,
                    "notes": manual_notes
                }
                
                try:
                    expense_id = st.session_state.expense_tracker.add_expense(expense_data)
                    st.success(f"✅ Expense saved! (ID: {expense_id})")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
            else:
                st.warning("⚠️ Please enter amount and vendor")

# PAGE 3: ANALYTICS
elif page == "📈 Analytics":
    st.header("Analytics & Insights")
    
    expenses_df = st.session_state.expense_tracker.get_all_expenses()
    
    if not expenses_df.empty:
        # Time range selector
        col1, col2 = st.columns(2)
        with col1:
            days_back = st.slider("Show data from last N days", 7, 365, 30)
        
        # Filter data
        cutoff_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
        filtered_df = expenses_df[expenses_df['date'] >= cutoff_date]
        
        # Spending trend
        st.subheader("Spending Trend Over Time")
        daily_spending = filtered_df.groupby('date')['amount'].sum().reset_index()
        
        fig_trend = px.line(
            daily_spending,
            x='date',
            y='amount',
            title="Daily Spending",
            markers=True
        )
        st.plotly_chart(fig_trend, use_container_width=True)
        
        # Category breakdown
        st.subheader("Category Analysis")
        col1, col2 = st.columns(2)
        
        with col1:
            category_data = filtered_df.groupby('category')['amount'].sum().sort_values(ascending=True)
            fig_category = px.barh(
                x=category_data.values,
                y=category_data.index,
                title="Spending by Category"
            )
            st.plotly_chart(fig_category, use_container_width=True)
        
        with col2:
            vendor_data = filtered_df.groupby('vendor')['amount'].sum().sort_values(ascending=False).head(10)
            fig_vendor = px.bar(
                x=vendor_data.index,
                y=vendor_data.values,
                title="Top 10 Vendors",
                labels={"x": "Vendor", "y": "Amount (₹)"}
            )
            st.plotly_chart(fig_vendor, use_container_width=True)
        
        # Statistics
        st.subheader("Statistics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Period Total", f"₹{filtered_df['amount'].sum():.2f}")
        
        with col2:
            st.metric("Average Daily", f"₹{filtered_df.groupby('date')['amount'].sum().mean():.2f}")
        
        with col3:
            st.metric("Max Transaction", f"₹{filtered_df['amount'].max():.2f}")
    else:
        st.info("No data to analyze. Add some expenses first!")

# PAGE 4: SETTINGS
elif page == "⚙️ Settings":
    st.header("Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Database")
        
        if st.button("📊 View Database Stats"):
            expenses_df = st.session_state.expense_tracker.get_all_expenses()
            st.write(f"Total expenses: {len(expenses_df)}")
            st.write(f"Total spent: ₹{expenses_df['amount'].sum():.2f}")
        
        if st.button("🗑️ Clear All Data (Caution!)"):
            if st.checkbox("I understand this will delete all data"):
                try:
                    st.session_state.expense_tracker.clear_all_expenses()
                    st.success("✅ All data cleared")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    with col2:
        st.subheader("About")
        st.info("""
        **Financial Advisor AI MVP**
        
        Version: 1.0
        Built with: Streamlit, Google Vision, Groq LLM
        
        Features:
        - 📸 OCR receipt scanning
        - 🤖 AI expense categorization
        - 📊 Expense tracking & analytics
        - 💡 Financial insights
        """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "Financial Advisor AI © 2026 | Built with ❤️ and AI"
    "</div>",
    unsafe_allow_html=True
)
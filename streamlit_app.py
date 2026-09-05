import streamlit as st
from groq import Groq
import tempfile
import os
from pathlib import Path
from ocr_engine import extract_text_from_image, analyze_expense_with_groq
from expense_tracker import ExpenseTracker
from config import GROQ_API_KEY, validate_config
import json

# Page config
st.set_page_config(page_title="Financial Advisor AI", layout="wide")

# Validate config on startup
try:
    validate_config()
except ValueError as e:
    st.error(f"Configuration Error: {e}")
    st.stop()

# Initialize Groq client
groq_client = Groq(api_key=GROQ_API_KEY)

# Initialize database
db = ExpenseTracker()

# Page title
st.title("💰 Financial Advisor AI")
st.subheader("AI-Powered Receipt & Expense Management")

# Create tabs
tab1, tab2, tab3 = st.tabs(["📸 Upload Receipt", "📊 View Expenses", "💡 Financial Insights"])

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
            db.add_expense(
                item_name=expense_data.get('item_name', 'Unknown'),
                amount=float(expense_data.get('amount', 0)),
                category=expense_data.get('category', 'Other'),
                date=expense_data.get('date', ''),
                vendor=expense_data.get('vendor', 'Unknown')
            )
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
    
    if not expenses:
        st.info("No expenses recorded yet. Upload a receipt to get started!")
    else:
        # Display as table
        import pandas as pd
        df = pd.DataFrame(expenses, columns=['ID', 'Item', 'Amount (₹)', 'Category', 'Date', 'Vendor'])
        st.dataframe(df, use_container_width=True)
        
        # Summary stats
        st.write("### Summary Statistics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total = sum([e[2] for e in expenses])
            st.metric("Total Spent", f"₹{total:.2f}")
        
        with col2:
            st.metric("Number of Expenses", len(expenses))
        
        with col3:
            avg = sum([e[2] for e in expenses]) / len(expenses) if expenses else 0
            st.metric("Average Expense", f"₹{avg:.2f}")
        
        # Category breakdown
        st.write("### Expenses by Category")
        category_totals = {}
        for expense in expenses:
            category = expense[4]  # Category column
            amount = expense[2]    # Amount column
            category_totals[category] = category_totals.get(category, 0) + amount
        
        import plotly.express as px
        fig = px.pie(
            names=list(category_totals.keys()),
            values=list(category_totals.values()),
            title="Expense Breakdown by Category"
        )
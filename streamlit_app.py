"""
Financial Advisor & Expense Manager MVP
AI-powered OCR expense extraction + dashboard + financial insights
Built with Streamlit, Google Vision API, and Groq LLM
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from ocr_engine import OCREngine
from expense_tracker import ExpenseTracker
import config

# ============ PAGE CONFIGURATION ============
st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon=config.APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============ CUSTOM STYLING ============
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
    }
    .success-text { color: #10b981; font-weight: bold; }
    .error-text { color: #ef4444; font-weight: bold; }
    .warning-text { color: #f59e0b; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ============ INITIALIZE SESSION STATE ============
if "expenses" not in st.session_state:
    st.session_state.expenses = None
if "tracker" not in st.session_state:
    st.session_state.tracker = ExpenseTracker()
if "ocr_engine" not in st.session_state:
    st.session_state.ocr_engine = OCREngine()

# ============ HELPER FUNCTIONS ============
def load_expenses():
    """Load all expenses from database"""
    return st.session_state.tracker.get_all_expenses()

def format_currency(amount, currency="INR"):
    """Format amount as currency"""
    if currency == "INR":
        return f"₹{amount:,.2f}"
    elif currency == "USD":
        return f"${amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"

def get_financial_advice(spending_data):
    """Get AI-powered financial advice based on spending"""
    try:
        from groq import Groq
        client = Groq(api_key=config.GROQ_API_KEY)
        
        prompt = f"""Based on this spending data, provide 2-3 concise financial tips:
- Total spent this month: ₹{spending_data.get('total', 0)}
- Top category: {spending_data.get('top_category', 'Unknown')} (₹{spending_data.get('top_amount', 0)})
- Number of transactions: {spending_data.get('count', 0)}

Provide practical, actionable advice for an Indian college student."""

        response = client.chat.completions.create(
            model=config.GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"Could not generate advice: {str(e)}"

# ============ MAIN SIDEBAR ============
with st.sidebar:
    st.title(config.APP_TITLE)
    
    st.markdown("---")
    
    # Navigation
    page = st.radio(
        "Navigation",
        ["📊 Dashboard", "📸 Add Expense (OCR)", "📋 Expenses List", "💡 Insights", "⚙️ Settings"]
    )
    
    st.markdown("---")
    
    # Quick stats
    df = load_expenses()
    if not df.empty:
        total_spent = df['amount'].sum()
        num_expenses = len(df)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Spent", format_currency(total_spent))
        with col2:
            st.metric("Transactions", num_expenses)
    else:
        st.info("No expenses yet. Start by adding an expense!")
    
    st.markdown("---")
    
    # Database info
    with st.expander("ℹ️ About", expanded=False):
        st.write(f"""
        **Financial Advisor MVP v1.0**
        
        - OCR-powered expense extraction
        - AI-powered financial insights
        - Spend tracking & analytics
        - Budget management
        
        **Tech Stack:**
        - Streamlit (UI)
        - Google Vision API (OCR)
        - Groq LLM (AI)
        - SQLite (Database)
        """)

# ============ PAGE: DASHBOARD ============
if page == "📊 Dashboard":
    st.header("📊 Dashboard")
    
    df = load_expenses()
    
    if df.empty:
        st.warning("📭 No expenses yet. Upload a receipt to get started!")
        st.stop()
    
    # Monthly summary
    month_summary = st.session_state.tracker.get_monthly_summary()
    
    if month_summary.get("breakdown"):
        # Header metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💰 Total This Month", format_currency(month_summary["total_spent"]))
        
        with col2:
            avg_expense = month_summary["total_spent"] / len(month_summary["breakdown"]) if month_summary["breakdown"] else 0
            st.metric("📈 Avg per Category", format_currency(avg_expense))
        
        with col3:
            st.metric("📊 Categories", len(month_summary["breakdown"]))
        
        with col4:
            num_trans = sum(c["count"] for c in month_summary["breakdown"])
            st.metric("📝 Transactions", num_trans)
        
        st.markdown("---")
        
        # Charts
        col1, col2 = st.columns(2)
        
        # Category breakdown
        with col1:
            st.subheader("Spending by Category")
            categories = [c["category"] for c in month_summary["breakdown"]]
            amounts = [c["amount"] for c in month_summary["breakdown"]]
            
            fig = px.pie(
                values=amounts, 
                names=categories,
                title="Monthly Breakdown"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Spending trend
        with col2:
            st.subheader("6-Month Trend")
            trend = st.session_state.tracker.get_spending_trend(6)
            
            if trend.get("months"):
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=trend["months"], 
                    y=trend["totals"],
                    mode='lines+markers',
                    name='Spending'
                ))
                fig.update_layout(
                    title="Last 6 Months",
                    xaxis_title="Month",
                    yaxis_title="Amount (₹)"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Financial advice
        st.subheader("💡 AI Financial Tips")
        spending_data = {
            "total": month_summary["total_spent"],
            "top_category": month_summary["breakdown"][0]["category"] if month_summary["breakdown"] else "Unknown",
            "top_amount": month_summary["breakdown"][0]["amount"] if month_summary["breakdown"] else 0,
            "count": sum(c["count"] for c in month_summary["breakdown"])
        }
        
        advice = get_financial_advice(spending_data)
        st.markdown(f"> {advice}")

# ============ PAGE: ADD EXPENSE (OCR) ============
elif page == "📸 Add Expense (OCR)":
    st.header("📸 Add Expense via Receipt OCR")
    
    st.write("Upload a receipt/payment screenshot and let AI extract the details!")
    
    uploaded_file = st.file_uploader("Choose a receipt image", type=["jpg", "jpeg", "png", "webp", "bmp"])
    
    if uploaded_file is not None:
        # Show preview
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Receipt Preview")
            st.image(uploaded_file, use_column_width=True)
        
        with col2:
            st.subheader("Processing...")
            
            with st.spinner("🔍 Extracting text from receipt..."):
                # Process image
                image_bytes = uploaded_file.read()
                result = st.session_state.ocr_engine.process_from_bytes(image_bytes)
            
            if result.get("success"):
                st.success("✅ Receipt processed successfully!")
                
                # Display extracted data
                st.subheader("Extracted Details")
                
                col_a, col_b = st.columns(2)
                
                with col_a:
                    amount = st.number_input(
                        "Amount",
                        value=float(result.get("amount", 0)),
                        min_value=0.0,
                        step=0.1
                    )
                    vendor = st.text_input(
                        "Vendor/Store",
                        value=result.get("vendor", "")
                    )
                    category = st.selectbox(
                        "Category",
                        config.EXPENSE_CATEGORIES,
                        index=0 if result.get("category", "Other") not in config.EXPENSE_CATEGORIES 
                              else config.EXPENSE_CATEGORIES.index(result.get("category", "Other"))
                    )
                
                with col_b:
                    currency = st.selectbox(
                        "Currency",
                        ["INR", "USD", "EUR"],
                        index=0
                    )
                    expense_date = st.date_input(
                        "Date",
                        value=datetime.now()
                    )
                    payment_method = st.selectbox(
                        "Payment Method",
                        ["card", "cash", "upi", "online", "unknown"]
                    )
                
                items_text = st.text_area(
                    "Items purchased (comma-separated)",
                    value=", ".join(result.get("items", [])) if result.get("items") else ""
                )
                
                notes = st.text_area(
                    "Additional notes",
                    value=result.get("notes", "")
                )
                
                # Save button
                if st.button("💾 Save Expense", use_container_width=True, type="primary"):
                    expense_data = {
                        "amount": amount,
                        "currency": currency,
                        "vendor": vendor,
                        "category": category,
                        "items": [item.strip() for item in items_text.split(",") if item.strip()],
                        "date": expense_date.strftime("%Y-%m-%d"),
                        "payment_method": payment_method,
                        "notes": notes,
                        "receipt_text": result.get("receipt_text", "")
                    }
                    
                    save_result = st.session_state.tracker.add_expense(expense_data)
                    
                    if save_result.get("success"):
                        st.success(f"✅ {save_result['message']}")
                        st.balloons()
                    else:
                        st.error(f"❌ {save_result.get('error')}")
            else:
                st.error(f"❌ Processing failed: {result.get('error')}")
                st.info("💡 Tip: Make sure the receipt is clear and well-lit")

# ============ PAGE: EXPENSES LIST ============
elif page == "📋 Expenses List":
    st.header("📋 All Expenses")
    
    df = load_expenses()
    
    if df.empty:
        st.info("No expenses recorded yet.")
    else:
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            categories = ["All"] + sorted(df["category"].unique().tolist())
            selected_category = st.selectbox("Filter by Category", categories)
        
        with col2:
            vendors = ["All"] + sorted(df["vendor"].unique().tolist())
            selected_vendor = st.selectbox("Filter by Vendor", vendors)
        
        with col3:
            sort_by = st.selectbox("Sort by", ["Date (Newest)", "Amount (High to Low)", "Amount (Low to High)"])
        
        # Apply filters
        filtered_df = df.copy()
        
        if selected_category != "All":
            filtered_df = filtered_df[filtered_df["category"] == selected_category]
        
        if selected_vendor != "All":
            filtered_df = filtered_df[filtered_df["vendor"] == selected_vendor]
        
        # Sort
        if sort_by == "Date (Newest)":
            filtered_df = filtered_df.sort_values("date", ascending=False)
        elif sort_by == "Amount (High to Low)":
            filtered_df = filtered_df.sort_values("amount", ascending=False)
        else:
            filtered_df = filtered_df.sort_values("amount", ascending=True)
        
        # Display table
        display_df = filtered_df[[
            "id", "date", "vendor", "category", "amount", "currency", "payment_method"
        ]].copy()
        display_df["amount"] = display_df.apply(
            lambda x: format_currency(x["amount"], x["currency"]), axis=1
        )
        display_df = display_df.drop("currency", axis=1)
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Export option
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total", format_currency(filtered_df["amount"].sum()))
        
        with col2:
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="📥 Download as CSV",
                data=csv,
                file_name=f"expenses_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

# ============ PAGE: INSIGHTS ============
elif page == "💡 Insights":
    st.header("💡 Financial Insights")
    
    df = load_expenses()
    
    if df.empty:
        st.warning("Add some expenses to see insights!")
    else:
        # Category analysis
        st.subheader("Top Spending Categories")
        cat_summary = st.session_state.tracker.get_expenses_by_category()
        
        if cat_summary.get("categories"):
            col1, col2 = st.columns([1, 1])
            
            with col1:
                fig = px.bar(
                    x=cat_summary["categories"],
                    y=cat_summary["totals"],
                    labels={"x": "Category", "y": "Amount (₹)"},
                    title="Top Spending Categories"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("Category Breakdown")
                for cat, total, count in zip(cat_summary["categories"], cat_summary["totals"], cat_summary["counts"]):
                    st.metric(cat, format_currency(total), f"{count} transactions")
        
        # Spending patterns
        st.subheader("Spending Patterns")
        
        trend = st.session_state.tracker.get_spending_trend(12)
        
        if trend.get("months"):
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=trend["months"],
                y=trend["totals"],
                name="Monthly Spending"
            ))
            fig.update_layout(
                title="12-Month Spending Trend",
                xaxis_title="Month",
                yaxis_title="Amount (₹)"
            )
            st.plotly_chart(fig, use_container_width=True)

# ============ PAGE: SETTINGS ============
elif page == "⚙️ Settings":
    st.header("⚙️ Settings")
    
    st.subheader("Database")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Database Path", config.DATABASE_PATH)
        
        if st.button("Refresh Data"):
            st.session_state.expenses = None
            st.success("✅ Data refreshed")
    
    with col2:
        # Export data
        if st.button("📥 Export All Expenses"):
            result = st.session_state.tracker.export_to_csv()
            if result.get("success"):
                st.success(result["message"])
            else:
                st.error(result.get("error"))
    
    st.markdown("---")
    
    st.subheader("API Status")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if config.GROQ_API_KEY:
            st.success("✅ Groq LLM: Connected")
        else:
            st.error("❌ Groq LLM: Not configured")
    
    with col2:
        if config.GOOGLE_VISION_API_KEY:
            st.success("✅ Google Vision: Connected")
        else:
            st.warning("⚠️ Google Vision: Not configured (OCR will be limited)")
    
    st.markdown("---")
    
    st.subheader("About")
    st.write(f"""
    **Financial Advisor & Expense Manager MVP**
    Version: 1.0.0
    
    Built with ❤️ for learning AI integration
    
    **Features:**
    - 📸 Receipt OCR using Google Vision API
    - 🤖 AI-powered expense categorization (Groq LLM)
    - 📊 Spending analytics and insights
    - 💾 SQLite database management
    - 📥 CSV export functionality
    
    **Technologies:**
    - Streamlit
    - Google Cloud Vision API
    - Groq AI API
    - SQLite
    - Pandas & Plotly
    """)

# ============ FOOTER ============
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 12px;'>
    Made with ❤️ | Financial Advisor MVP | Powered by Streamlit, Google Vision & Groq AI
</div>
""", unsafe_allow_html=True)

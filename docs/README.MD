# 💰 Financial Advisor AI

AI-Powered Receipt OCR & Expense Management System

## ✨ Features

### 📸 Receipt Upload & OCR
- Upload receipt images (JPG, PNG, BMP)
- Automatic text extraction with EasyOCR
- AI-powered expense categorization
- Manual entry option for quick logging

### 📊 Expense Dashboard
- View all expenses in organized table
- Category-wise breakdown (pie charts)
- Summary statistics (total, average, count)
- Real-time analytics

### 💡 Financial Insights
- AI-generated spending analysis
- Personalized recommendations
- Actionable tips for savings
- Pattern recognition

### 🧠 Financial Advisor
- Warren Buffett principles
- Robert Kiyosaki strategies
- Ramit Sethi tips
- Indian financial context
- Guru comparison tool

### 💰 Tax Calculator (FY 2024-25)
- Income tax calculation
- Deduction support: 80C, 80D, 80E, 80CCD
- Old regime tax slabs
- Net income projection

### 📈 SIP Calculator
- Monthly investment projections
- Year-by-year breakdown
- Growth visualization
- ROI calculations

---

## 🔒 Security

### Encryption
- **Database Encryption:** AES-256 encrypted SQLite database
- **Key Management:** Encryption key stored in .env (never in code)
- **At-Rest Protection:** Expenses encrypted before storage

### API Security
- **No Key Exposure:** API keys kept in environment variables
- **Rate Limiting:** Cached LLM responses to avoid hitting limits
- **Prompt Injection Testing:** LLM tested against malicious inputs ✅

### Data Privacy
- **No Cloud Storage:** Data stays local by default
- **User Control:** Manual entry + receipt upload
- **Deletion:** Users can delete expenses anytime
- **Compliance:** GDPR-compliant data handling

---

## 🚀 Deployment

### Local Setup
```bash
# Clone repo
git clone <your-repo>
cd financial-advisor-ai

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt --break-system-packages

# Set up .env
copy .env.example .env
# Add: GROQ_API_KEY=your_key_here
# Add: ENCRYPTION_KEY=your_key_here

# Run app
streamlit run streamlit_app.py
```

### Deploy to Streamlit Cloud
1. Push code to GitHub
2. Go to https://share.streamlit.io/
3. Click "New App"
4. Select repo: `financial-advisor-ai`
5. Set main file: `frontend/streamlit_app.py`
6. Add secrets:
   - GROQ_API_KEY
   - ENCRYPTION_KEY
7. Deploy!

---

## 📋 Tech Stack
- **Frontend:** Streamlit
- **Backend:** Python
- **OCR:** EasyOCR
- **LLM:** Groq (Qwen 3.8)
- **Database:** SQLite
- **Encryption:** Cryptography (Fernet)
- **Visualization:** Plotly

---

## 📝 License
MIT License
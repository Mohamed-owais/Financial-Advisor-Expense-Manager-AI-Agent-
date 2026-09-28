# API Key Security Guide

## 1. Never Commit API Keys

Add to `.gitignore`:
.env
.env.local
.encryption_key
*.pyc
pycache/

## 2. Verify No Keys in Code

Run this to check:
```bash
grep -r "GROQ_API_KEY" --include="*.py" .
grep -r "sk-" --include="*.py" .
```

Should return nothing (only in .env file).

## 3. Environment Variables Only

✅ **CORRECT:**
```python
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)
```

❌ **WRONG:**
```python
client = Groq(api_key="gsk_xxxxxxxxxxxx")
```

## 4. For Production (Streamlit Cloud)

Use Streamlit Secrets, NOT .env:
1. Go to: https://share.streamlit.io/
2. Select app → Settings
3. Add secrets:
GROQ_API_KEY = "your-key-here"
ENCRYPTION_KEY = "your-key-here"

## 5. Key Rotation

If key is exposed:
1. Revoke old key in Groq console
2. Generate new key
3. Update .env and Streamlit Secrets
4. Redeploy app

## 6. Logging Best Practices

Never log API calls with keys:
```python
# ❌ WRONG
print(f"API Key: {api_key}")
print(f"Response: {response}")

# ✅ CORRECT
print("API call successful")
logger.info("Groq API called", extra={"model": "qwen"})
```

## Checklist
- [ ] No keys in code
- [ ] .env in .gitignore
- [ ] Only use os.getenv()
- [ ] Secrets in Streamlit (production)
- [ ] No sensitive logging.
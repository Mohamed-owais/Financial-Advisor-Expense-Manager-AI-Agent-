from cryptography.fernet import Fernet
import os
from pathlib import Path

class DatabaseEncryption:
    """Encrypt/Decrypt SQLite database"""
    
    def __init__(self, key_file=".encryption_key"):
        self.key_file = key_file
        self.key = self._load_or_create_key()
        self.cipher = Fernet(self.key)
    
    def _load_or_create_key(self):
        """Load key from .env or create new one"""
        # Try to get from Streamlit secrets first (production)
        try:
            return os.getenv("ENCRYPTION_KEY").encode()
        except:
            pass
        
        # Try to load from file (development)
        if os.path.exists(self.key_file):
            with open(self.key_file, "rb") as f:
                return f.read()
        
        # Create new key
        new_key = Fernet.generate_key()
        with open(self.key_file, "wb") as f:
            f.write(new_key)
        print(f"⚠️ New encryption key created: {self.key_file}")
        print("⚠️ ADD TO .env: ENCRYPTION_KEY=<copy key contents>")
        return new_key
    
    def encrypt_file(self, file_path):
        """Encrypt a file (database)"""
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return False
        
        with open(file_path, "rb") as f:
            data = f.read()
        
        encrypted_data = self.cipher.encrypt(data)
        
        with open(file_path + ".encrypted", "wb") as f:
            f.write(encrypted_data)
        
        # Delete original
        os.remove(file_path)
        print(f"✅ Encrypted: {file_path}")
        return True
    
    def decrypt_file(self, encrypted_file_path, output_path):
        """Decrypt a file"""
        if not os.path.exists(encrypted_file_path):
            print(f"Encrypted file not found: {encrypted_file_path}")
            return False
        
        with open(encrypted_file_path, "rb") as f:
            encrypted_data = f.read()
        
        try:
            decrypted_data = self.cipher.decrypt(encrypted_data)
            with open(output_path, "wb") as f:
                f.write(decrypted_data)
            print(f"✅ Decrypted: {output_path}")
            return True
        except Exception as e:
            print(f"❌ Decryption failed: {str(e)}")
            return False
    
    def encrypt_database_at_rest(self, db_path="expenses.db"):
        """Encrypt database file for storage"""
        if os.path.exists(db_path):
            self.encrypt_file(db_path)
    
    def decrypt_database_on_startup(self, encrypted_db="expenses.db.encrypted", db_path="expenses.db"):
        """Decrypt database on app startup"""
        if os.path.exists(encrypted_db) and not os.path.exists(db_path):
            self.decrypt_file(encrypted_db, db_path)
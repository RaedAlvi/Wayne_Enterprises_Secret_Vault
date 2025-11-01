"""
Generate FERNET_KEY for encryption
Run this once and save the key to your .env file
"""
from cryptography.fernet import Fernet

key = Fernet.generate_key().decode()
print("\n" + "="*60)
print("🔐 WAYNE ENTERPRISES SECRET VAULT - ENCRYPTION KEY")
print("="*60)
print(f"\nYour FERNET_KEY:\n\n{key}\n")
print("⚠️  IMPORTANT: Save this key securely!")
print("⚠️  Add it to your .env file as: FERNET_KEY=" + key)
print("⚠️  Never share this key or commit it to version control!")
print("\n" + "="*60 + "\n")

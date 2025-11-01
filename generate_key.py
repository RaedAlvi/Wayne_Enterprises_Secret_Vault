from cryptography.fernet import Fernet

# Generate the key
key = Fernet.generate_key()

# Print the key as a string (this is what you'll put in .env)
print(key.decode())

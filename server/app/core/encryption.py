from cryptography.fernet import Fernet

from app.core.config import settings

# Handles encryption and decryption of sensitive data.
fernet = Fernet(settings.LASTFM_ENCRYPTION_KEY.encode())


# Encrypts a Last.fm session key.
def encrypt_session_key(session_key: str) -> str:
    encrypted_key = fernet.encrypt(session_key.encode())
    return encrypted_key.decode()


# Decrypts a Last.fm session key.
def decrypt_session_key(encrypted_key: str) -> str:
    decrypted_key = fernet.decrypt(encrypted_key.encode())
    return decrypted_key.decode()

import pytest
from cryptography.fernet import InvalidToken

from app.core.encryption import decrypt_session_key, encrypt_session_key


# Tests that session keys are encrypted before storage.
def test_encrypt_session_key():
    session_key = "test_lastfm_session_key"

    encrypted_key = encrypt_session_key(session_key)

    assert encrypted_key != session_key


# Tests that encrypted session keys can be decrypted.
def test_decrypt_session_key():
    session_key = "test_lastfm_session_key"

    encrypted_key = encrypt_session_key(session_key)
    decrypted_key = decrypt_session_key(encrypted_key)

    assert decrypted_key == session_key


# Tests that encrypting the same session key produces different ciphertexts.
def test_encrypt_session_key_produces_unique_ciphertext():
    session_key = "test_lastfm_session_key"

    first_encryption = encrypt_session_key(session_key)
    second_encryption = encrypt_session_key(session_key)

    assert first_encryption != second_encryption


# Tests that invalid encrypted session keys are rejected.
def test_decrypt_invalid_session_key():
    with pytest.raises(InvalidToken):
        decrypt_session_key("invalid_encrypted_key")

from pwdlib import PasswordHash

# selects a recommended password-hashing config
password_hash = PasswordHash.recommended()


# converts a plaintext password into a secure hash
def hash_password(password: str) -> str:
    return password_hash.hash(password)


# checks whether a submitted password matches the stored hash
def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)

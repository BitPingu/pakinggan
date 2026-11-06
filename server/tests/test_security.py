from app.core.security import hash_password, verify_password


def test_hash_password():
    password = "test-password"

    hashed_password = hash_password(password)

    assert hashed_password != password
    assert hashed_password.startswith("$argon2")


def test_verify_password():
    password = "test-password"

    hashed_password = hash_password(password)

    assert verify_password(password, hashed_password)


def test_verify_incorrect_password():
    hashed_password = hash_password("test-password")

    assert not verify_password("wrong-password", hashed_password)

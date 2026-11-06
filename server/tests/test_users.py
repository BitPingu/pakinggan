from app.core.security import verify_password
from app.models.user import User


# successful user registration
def test_create_user(client, db_session):
    response = client.post(
        "/api/users/",
        json={
            "username": "gavin",
            "email": "gavin@example.com",
            "password": "securepassword123",
        },
    )

    assert response.status_code == 201

    # verify account creation
    data = response.json()

    assert data["username"] == "gavin"
    assert data["email"] == "gavin@example.com"

    # passwords shouldn't be exposed
    assert "password" not in data
    assert "hashed_password" not in data

    user = db_session.query(User).filter(User.username == "gavin").first()

    assert user is not None
    assert user.hashed_password != "securepassword123"


# duplicate usernames
def test_create_user_duplicate_username(client, user):
    response = client.post(
        "/api/users/",
        json={
            "username": user["username"],
            "email": "another@example.com",
            "password": "securepassword123",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Username or email already registered"


# duplicate email addresses
def test_create_user_duplicate_email(client, user):
    response = client.post(
        "/api/users/",
        json={
            "username": "another_user",
            "email": user["email"],
            "password": "securepassword123",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Username or email already registered"


# password validation
def test_create_user_short_password(client):
    response = client.post(
        "/api/users/",
        json={
            "username": "another_user",
            "email": "another@example.com",
            "password": "short",
        },
    )

    # rejected by min_length=8
    assert response.status_code == 422


# whitespace name
def test_create_user_whitespace_username(client):
    response = client.post(
        "/api/users/",
        json={
            "username": "   ",
            "email": "another@example.com",
            "password": "securepassword123",
        },
    )

    # rejected by trim
    assert response.status_code == 422


# whitespace trimming
def test_create_user_trims_username(client):
    response = client.post(
        "/api/users/",
        json={
            "username": "  gavin  ",
            "email": "gavin@example.com",
            "password": "securepassword123",
        },
    )

    assert response.status_code == 201
    assert response.json()["username"] == "gavin"


# invalid email address
def test_create_user_invalid_email(client):
    response = client.post(
        "/api/users/",
        json={
            "username": "gavin",
            "email": "not-an-email",
            "password": "securepassword123",
        },
    )

    assert response.status_code == 422


# username too short
def test_create_user_username_too_short(client):
    response = client.post(
        "/api/users/",
        json={
            "username": "ab",
            "email": "gavin@example.com",
            "password": "securepassword123",
        },
    )

    # rejected by min_length=3
    assert response.status_code == 422


# username too long
def test_create_user_username_too_long(client):
    response = client.post(
        "/api/users/",
        json={
            "username": "a" * 51,
            "email": "gavin@example.com",
            "password": "securepassword123",
        },
    )

    # rejected by max_length=50
    assert response.status_code == 422


# password verification
def test_create_user_password_hash(client, db_session):
    client.post(
        "/api/users/",
        json={
            "username": "gavin",
            "email": "gavin@example.com",
            "password": "securepassword123",
        },
    )

    user = db_session.query(User).filter(User.username == "gavin").first()

    assert user is not None
    assert verify_password("securepassword123", user.hashed_password)  # successful
    assert not verify_password("wrong-password", user.hashed_password)  # unsuccessful

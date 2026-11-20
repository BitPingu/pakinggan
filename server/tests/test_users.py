from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from app.core.security import (
    decode_access_token,
    hash_password_reset_token,
    verify_password,
)
from app.models.user import User

FORGOT_PASSWORD_MESSAGE = (
    "If an account exists with that email, a password-reset link will be sent."
)


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


# valid credentials return an access token
def test_login_success(client, user):
    response = client.post(
        "/api/users/login",
        json={
            "username": "gavin",
            "password": "securepassword123",
        },
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


# an incorrect password returns 401
def test_login_incorrect_password(client, user):
    response = client.post(
        "/api/users/login",
        json={
            "username": "gavin",
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"


# a nonexistent username also returns 401
def test_login_nonexistent_user(client):
    response = client.post(
        "/api/users/login",
        json={
            "username": "unknown",
            "password": "securepassword123",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"


# user can retrieve their own profile (valid token)
def test_get_current_user(client, user):
    response = client.post(
        "/api/users/login",
        json={
            "username": "gavin",
            "password": "securepassword123",
        },
    )

    token = response.json()["access_token"]

    response = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["id"] == user["id"]
    assert response.json()["username"] == user["username"]


# request is rejected (no token)
def test_get_current_user_unauthenticated(client):
    response = client.get("/api/users/me")

    assert response.status_code == 401


# request is rejected (invalid token)
def test_get_current_user_invalid_token(client):
    response = client.get(
        "/api/users/me",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401


# access tokens include the user's current token version
def test_login_token_version(client, user):
    response = client.post(
        "/api/users/login",
        json={
            "username": "gavin",
            "password": "securepassword123",
        },
    )

    token = response.json()["access_token"]

    payload = decode_access_token(token)

    assert payload["ver"] == 0


# previously issued access tokens are rejected after token version changes
def test_get_current_user_invalidated_token(client, user, db_session):
    response = client.post(
        "/api/users/login",
        json={
            "username": "gavin",
            "password": "securepassword123",
        },
    )

    token = response.json()["access_token"]

    user_record = db_session.query(User).filter(User.id == user["id"]).first()
    user_record.token_version += 1
    db_session.commit()

    response = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


# An existing email generates a reset token and sends a reset email.
@patch("app.routers.users.send_password_reset_email")
def test_forgot_password_existing_email(mock_send_email, client, user, db_session):
    response = client.post(
        "/api/users/forgot-password",
        json={"email": user["email"]},
    )

    assert response.status_code == 200
    assert response.json() == {"message": FORGOT_PASSWORD_MESSAGE}

    # Verifies that a reset token was stored as a hash.
    user_record = db_session.query(User).filter(User.id == user["id"]).first()

    assert user_record.password_reset_token_hash is not None
    assert len(user_record.password_reset_token_hash) == 64

    # Verifies that the reset token expires in approximately 30 minutes.
    assert user_record.password_reset_expires_at is not None

    expiration = user_record.password_reset_expires_at
    if expiration.tzinfo is None:
        expiration = expiration.replace(tzinfo=timezone.utc)

    remaining_time = expiration - datetime.now(timezone.utc)

    assert timedelta(minutes=29) < remaining_time <= timedelta(minutes=30)

    # Verifies that the reset email contains the generated link.
    mock_send_email.assert_called_once()

    recipient, reset_url = mock_send_email.call_args.args

    assert recipient == user["email"]
    assert "reset-password?token=" in reset_url

    # The plaintext token is not stored in the database.
    token = reset_url.split("token=", 1)[1]
    assert user_record.password_reset_token_hash == (hash_password_reset_token(token))


# A nonexistent email receives the same generic response.
@patch("app.routers.users.send_password_reset_email")
def test_forgot_password_nonexistent_email(mock_send_email, client):
    response = client.post(
        "/api/users/forgot-password",
        json={"email": "unknown@example.com"},
    )

    assert response.status_code == 200
    assert response.json() == {"message": FORGOT_PASSWORD_MESSAGE}

    # No email is sent when the account does not exist.
    mock_send_email.assert_not_called()


# Invalid email addresses are rejected.
def test_forgot_password_invalid_email(client):
    response = client.post(
        "/api/users/forgot-password",
        json={"email": "not-an-email"},
    )

    assert response.status_code == 422


# Email delivery failures do not expose account information.
@patch(
    "app.routers.users.send_password_reset_email",
    side_effect=Exception("SMTP connection failed"),
)
def test_forgot_password_email_failure(mock_send_email, client, user):
    response = client.post(
        "/api/users/forgot-password",
        json={"email": user["email"]},
    )

    assert response.status_code == 200
    assert response.json() == {"message": FORGOT_PASSWORD_MESSAGE}

    mock_send_email.assert_called_once()


# A valid reset token allows a user to reset their password.
def test_reset_password_success(client, user, db_session):
    token = "valid-reset-token"

    user_record = db_session.query(User).filter(User.id == user["id"]).first()
    user_record.password_reset_token_hash = hash_password_reset_token(token)
    user_record.password_reset_expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=30
    )
    db_session.commit()

    response = client.post(
        "/api/users/reset-password",
        json={
            "token": token,
            "new_password": "newsecurepassword123",
        },
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Your password has been reset successfully."}

    db_session.refresh(user_record)

    assert verify_password("newsecurepassword123", user_record.hashed_password)
    assert user_record.password_reset_token_hash is None
    assert user_record.password_reset_expires_at is None
    assert user_record.token_version == 1


# An invalid reset token is rejected.
def test_reset_password_invalid_token(client):
    response = client.post(
        "/api/users/reset-password",
        json={
            "token": "invalid-reset-token",
            "new_password": "newsecurepassword123",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid or expired password-reset token"


# An expired reset token is rejected.
def test_reset_password_expired_token(client, user, db_session):
    token = "expired-reset-token"

    user_record = db_session.query(User).filter(User.id == user["id"]).first()
    user_record.password_reset_token_hash = hash_password_reset_token(token)
    user_record.password_reset_expires_at = datetime.now(timezone.utc) - timedelta(
        minutes=1
    )
    db_session.commit()

    response = client.post(
        "/api/users/reset-password",
        json={
            "token": token,
            "new_password": "newsecurepassword123",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid or expired password-reset token"


# A reset token cannot be reused after a successful password reset.
def test_reset_password_token_reuse(client, user, db_session):
    token = "single-use-reset-token"

    user_record = db_session.query(User).filter(User.id == user["id"]).first()
    user_record.password_reset_token_hash = hash_password_reset_token(token)
    user_record.password_reset_expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=30
    )
    db_session.commit()

    payload = {
        "token": token,
        "new_password": "newsecurepassword123",
    }

    first_response = client.post("/api/users/reset-password", json=payload)
    second_response = client.post("/api/users/reset-password", json=payload)

    assert first_response.status_code == 200
    assert second_response.status_code == 400


# The new password works and the old password no longer works.
def test_reset_password_login(client, user, db_session):
    token = "login-reset-token"

    user_record = db_session.query(User).filter(User.id == user["id"]).first()
    user_record.password_reset_token_hash = hash_password_reset_token(token)
    user_record.password_reset_expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=30
    )
    db_session.commit()

    reset_response = client.post(
        "/api/users/reset-password",
        json={
            "token": token,
            "new_password": "newsecurepassword123",
        },
    )

    assert reset_response.status_code == 200

    new_login = client.post(
        "/api/users/login",
        json={
            "username": user["username"],
            "password": "newsecurepassword123",
        },
    )

    old_login = client.post(
        "/api/users/login",
        json={
            "username": user["username"],
            "password": "securepassword123",
        },
    )

    assert new_login.status_code == 200
    assert old_login.status_code == 401


# Password reset invalidates previously issued access tokens.
def test_reset_password_invalidates_access_token(client, user, db_session):
    login_response = client.post(
        "/api/users/login",
        json={
            "username": user["username"],
            "password": "securepassword123",
        },
    )

    access_token = login_response.json()["access_token"]

    token = "session-reset-token"

    user_record = db_session.query(User).filter(User.id == user["id"]).first()
    user_record.password_reset_token_hash = hash_password_reset_token(token)
    user_record.password_reset_expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=30
    )
    db_session.commit()

    reset_response = client.post(
        "/api/users/reset-password",
        json={
            "token": token,
            "new_password": "newsecurepassword123",
        },
    )

    assert reset_response.status_code == 200

    profile_response = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert profile_response.status_code == 401


# An authenticated user can delete their account with the correct password.
def test_delete_account_success(client, user, db_session):
    login_response = client.post(
        "/api/users/login",
        json={
            "username": user["username"],
            "password": "securepassword123",
        },
    )

    token = login_response.json()["access_token"]

    response = client.request(
        "DELETE",
        "/api/users/me",
        json={"password": "securepassword123"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 204
    assert response.content == b""

    deleted_user = db_session.query(User).filter(User.id == user["id"]).first()

    assert deleted_user is None


# An incorrect password prevents account deletion.
def test_delete_account_incorrect_password(client, user, db_session):
    login_response = client.post(
        "/api/users/login",
        json={
            "username": user["username"],
            "password": "securepassword123",
        },
    )

    token = login_response.json()["access_token"]

    response = client.request(
        "DELETE",
        "/api/users/me",
        json={"password": "wrongpassword"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect password"

    existing_user = db_session.query(User).filter(User.id == user["id"]).first()

    assert existing_user is not None


# Account deletion requires authentication.
def test_delete_account_unauthenticated(client, user):
    response = client.request(
        "DELETE",
        "/api/users/me",
        json={"password": "securepassword123"},
    )

    assert response.status_code == 401


# A deleted account can no longer authenticate.
def test_delete_account_cannot_login(client, user):
    login_response = client.post(
        "/api/users/login",
        json={
            "username": user["username"],
            "password": "securepassword123",
        },
    )

    token = login_response.json()["access_token"]

    delete_response = client.request(
        "DELETE",
        "/api/users/me",
        json={"password": "securepassword123"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert delete_response.status_code == 204

    login_response = client.post(
        "/api/users/login",
        json={
            "username": user["username"],
            "password": "securepassword123",
        },
    )

    assert login_response.status_code == 401


# An authenticated user can change their password with the correct current password.
def test_change_password_success(client, user, db_session):
    login_response = client.post(
        "/api/users/login",
        json={
            "username": user["username"],
            "password": "securepassword123",
        },
    )

    token = login_response.json()["access_token"]

    response = client.put(
        "/api/users/me/password",
        json={
            "current_password": "securepassword123",
            "new_password": "newsecurepassword123",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Your password has been changed successfully."
    }

    user_record = db_session.query(User).filter(User.id == user["id"]).first()

    assert verify_password("newsecurepassword123", user_record.hashed_password)
    assert user_record.token_version == 1
    assert user_record.password_reset_token_hash is None
    assert user_record.password_reset_expires_at is None


# An incorrect current password prevents a password change.
def test_change_password_incorrect_password(client, user, db_session):
    login_response = client.post(
        "/api/users/login",
        json={
            "username": user["username"],
            "password": "securepassword123",
        },
    )

    token = login_response.json()["access_token"]

    response = client.put(
        "/api/users/me/password",
        json={
            "current_password": "wrongpassword",
            "new_password": "newsecurepassword123",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect password"

    user_record = db_session.query(User).filter(User.id == user["id"]).first()

    assert verify_password("securepassword123", user_record.hashed_password)
    assert user_record.token_version == 0


# A user cannot change their password to its existing value.
def test_change_password_same_password(client, user):
    login_response = client.post(
        "/api/users/login",
        json={
            "username": user["username"],
            "password": "securepassword123",
        },
    )

    token = login_response.json()["access_token"]

    response = client.put(
        "/api/users/me/password",
        json={
            "current_password": "securepassword123",
            "new_password": "securepassword123",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "New password must be different from the current password"
    )


# Password changes require authentication.
def test_change_password_unauthenticated(client):
    response = client.put(
        "/api/users/me/password",
        json={
            "current_password": "securepassword123",
            "new_password": "newsecurepassword123",
        },
    )

    assert response.status_code == 401


# A new password must meet the minimum length requirement.
def test_change_password_short_new_password(client, user):
    login_response = client.post(
        "/api/users/login",
        json={
            "username": user["username"],
            "password": "securepassword123",
        },
    )

    token = login_response.json()["access_token"]

    response = client.put(
        "/api/users/me/password",
        json={
            "current_password": "securepassword123",
            "new_password": "short",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 422


# The new password works and the old password no longer works.
def test_change_password_login(client, user):
    login_response = client.post(
        "/api/users/login",
        json={
            "username": user["username"],
            "password": "securepassword123",
        },
    )

    token = login_response.json()["access_token"]

    change_response = client.put(
        "/api/users/me/password",
        json={
            "current_password": "securepassword123",
            "new_password": "newsecurepassword123",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert change_response.status_code == 200

    new_login = client.post(
        "/api/users/login",
        json={
            "username": user["username"],
            "password": "newsecurepassword123",
        },
    )

    old_login = client.post(
        "/api/users/login",
        json={
            "username": user["username"],
            "password": "securepassword123",
        },
    )

    assert new_login.status_code == 200
    assert old_login.status_code == 401


# Changing a password invalidates previously issued access tokens.
def test_change_password_invalidates_access_token(client, user):
    login_response = client.post(
        "/api/users/login",
        json={
            "username": user["username"],
            "password": "securepassword123",
        },
    )

    access_token = login_response.json()["access_token"]

    change_response = client.put(
        "/api/users/me/password",
        json={
            "current_password": "securepassword123",
            "new_password": "newsecurepassword123",
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert change_response.status_code == 200

    profile_response = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert profile_response.status_code == 401


# Changing a password invalidates any outstanding password-reset token.
def test_change_password_invalidates_reset_token(client, user, db_session):
    token = "outstanding-reset-token"

    user_record = db_session.query(User).filter(User.id == user["id"]).first()
    user_record.password_reset_token_hash = hash_password_reset_token(token)
    user_record.password_reset_expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=30
    )
    db_session.commit()

    login_response = client.post(
        "/api/users/login",
        json={
            "username": user["username"],
            "password": "securepassword123",
        },
    )

    access_token = login_response.json()["access_token"]

    response = client.put(
        "/api/users/me/password",
        json={
            "current_password": "securepassword123",
            "new_password": "newsecurepassword123",
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200

    reset_response = client.post(
        "/api/users/reset-password",
        json={
            "token": token,
            "new_password": "anothersecurepassword123",
        },
    )

    assert reset_response.status_code == 400


# An authenticated user can change their email with the correct password.
def test_change_email_success(client, user, db_session):
    login_response = client.post(
        "/api/users/login",
        json={
            "username": user["username"],
            "password": "securepassword123",
        },
    )

    token = login_response.json()["access_token"]

    response = client.put(
        "/api/users/me/email",
        json={
            "email": "newemail@example.com",
            "current_password": "securepassword123",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Your email has been changed successfully."}

    user_record = db_session.query(User).filter(User.id == user["id"]).first()

    assert user_record.email == "newemail@example.com"
    assert user_record.token_version == 0


# An incorrect current password prevents an email change.
def test_change_email_incorrect_password(client, user, db_session):
    login_response = client.post(
        "/api/users/login",
        json={
            "username": user["username"],
            "password": "securepassword123",
        },
    )

    token = login_response.json()["access_token"]

    response = client.put(
        "/api/users/me/email",
        json={
            "email": "newemail@example.com",
            "current_password": "wrongpassword",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect password"

    user_record = db_session.query(User).filter(User.id == user["id"]).first()

    assert user_record.email == user["email"]


# A user cannot change their email to its existing value.
def test_change_email_same_email(client, user):
    login_response = client.post(
        "/api/users/login",
        json={
            "username": user["username"],
            "password": "securepassword123",
        },
    )

    token = login_response.json()["access_token"]

    response = client.put(
        "/api/users/me/email",
        json={
            "email": user["email"],
            "current_password": "securepassword123",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "New email must be different from the current email"
    )


# A user cannot change their email to one already registered.
def test_change_email_duplicate_email(client, user, db_session):
    client.post(
        "/api/users/",
        json={
            "username": "another_user",
            "email": "existing@example.com",
            "password": "securepassword123",
        },
    )

    login_response = client.post(
        "/api/users/login",
        json={
            "username": user["username"],
            "password": "securepassword123",
        },
    )

    token = login_response.json()["access_token"]

    response = client.put(
        "/api/users/me/email",
        json={
            "email": "existing@example.com",
            "current_password": "securepassword123",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Email already registered"

    user_record = db_session.query(User).filter(User.id == user["id"]).first()

    assert user_record.email == user["email"]


# Email changes require authentication.
def test_change_email_unauthenticated(client):
    response = client.put(
        "/api/users/me/email",
        json={
            "email": "newemail@example.com",
            "current_password": "securepassword123",
        },
    )

    assert response.status_code == 401


# Invalid email addresses are rejected.
def test_change_email_invalid_email(client, user):
    login_response = client.post(
        "/api/users/login",
        json={
            "username": user["username"],
            "password": "securepassword123",
        },
    )

    token = login_response.json()["access_token"]

    response = client.put(
        "/api/users/me/email",
        json={
            "email": "not-an-email",
            "current_password": "securepassword123",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 422


# Changing an email invalidates any outstanding password-reset token.
def test_change_email_invalidates_reset_token(client, user, db_session):
    token = "outstanding-reset-token"

    user_record = db_session.query(User).filter(User.id == user["id"]).first()
    user_record.password_reset_token_hash = hash_password_reset_token(token)
    user_record.password_reset_expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=30
    )
    db_session.commit()

    login_response = client.post(
        "/api/users/login",
        json={
            "username": user["username"],
            "password": "securepassword123",
        },
    )

    access_token = login_response.json()["access_token"]

    response = client.put(
        "/api/users/me/email",
        json={
            "email": "newemail@example.com",
            "current_password": "securepassword123",
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200

    db_session.refresh(user_record)

    assert user_record.password_reset_token_hash is None
    assert user_record.password_reset_expires_at is None

    reset_response = client.post(
        "/api/users/reset-password",
        json={
            "token": token,
            "new_password": "anothersecurepassword123",
        },
    )

    assert reset_response.status_code == 400

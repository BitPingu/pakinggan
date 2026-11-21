import smtplib
from email.message import EmailMessage

from app.core.config import settings


# Sends a password-reset email containing the generated reset link.
def send_password_reset_email(recipient_email: str, reset_url: str) -> None:
    message = EmailMessage()
    message["Subject"] = "Reset your pakinggan password"
    message["From"] = settings.SMTP_FROM_EMAIL
    message["To"] = recipient_email

    message.set_content(
        f"""Hello,

We received a request to reset your pakinggan password.

Use the link below to choose a new password:

{reset_url}

This link expires in 30 minutes. If you did not request a password reset,
you can safely ignore this email.

The pakinggan team
"""
    )

    # Connects to the configured SMTP server and sends the email.
    with smtplib.SMTP(
        settings.SMTP_HOST,
        settings.SMTP_PORT,
        timeout=10,
    ) as server:
        if settings.SMTP_USE_TLS:
            server.starttls()

        if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)

        server.send_message(message)

from django.core.mail import send_mail
from django.conf import settings
from textwrap import dedent


def send_password_reset_email(user, reset_token):
    """
    Sends a password reset email to the user.

    This function generates an email containing a link that the user can
    click to reset their password. The email includes both an HTML and
    plain text version for compatibility with various email clients.

    Args:
        user: The user object for whom the password reset was requested.
        reset_token: A unique token used to identify
        the password reset request.

    The email contains:
    - Subject: "Password Reset Request - Local Listing"
    - HTML and plain text message formats
    - A reset link that directs the user to reset their password
    """

    subject = 'Password Reset Request - Local Listing'
    reset_url = f"{settings.FRONTEND_URL}/reset-password/{reset_token}"

    # HTML Message
    html_message = dedent(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6;
            color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Password Reset Request</h2>
            <p>Hello {user.username},</p>
            <p>A password reset was requested for your
            Local Listing account.</p>
            <p>To reset your password, click the link below:</p>
            <p><a href="{reset_url}">{reset_url}</a></p>
            <p>If you can't click the link,
            copy and paste it into your browser.</p>
            <p>If you didn't request this, please ignore this email or contact
            support if you have concerns.</p>
            <p>Thank you,<br>The Local Listing Team</p>
        </div>
    </body>
    </html>
    """)

    # Plain text message (as a fallback)
    plain_message = dedent(f"""
    Password Reset Request - Local Listing

    Hello {user.username},

    A password reset was requested for your Local Listing account.
    To reset your password, copy and paste the following link
    into your browser:

    {reset_url}

    If you didn't request this, please ignore this email or contact support
    if you have concerns.

    Thank you,
    The Local Listing Team
    """)

    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = user.email

    send_mail(
        subject,
        plain_message,
        from_email,
        [to_email],
        html_message=html_message,
    )

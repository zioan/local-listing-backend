from django.core.mail import send_mail
from django.conf import settings


def send_password_reset_email(user, reset_token):
    subject = 'Password Reset Request'
    reset_url = f"{settings.FRONTEND_URL}/reset-password/{reset_token}"
    message = f"""
    You've requested to reset your password. 
    Please click on the link below to reset your password:
    
    {reset_url}
    
    If you didn't request this, you can safely ignore this email.
    """
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = user.email

    send_mail(subject, message, from_email, [to_email])

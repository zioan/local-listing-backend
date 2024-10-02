from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from django.db import models
from django.utils import timezone
import uuid


class CustomUserManager(BaseUserManager):
    """
    Custom manager for the CustomUser model.

    Provides helper methods to create regular users and superusers.
    It normalizes the email, sets the password, and handles extra fields.
    """

    def create_user(self, email, username, password=None, **extra_fields):
        """
        Create and return a regular user with an email, username, and password.

        Raises:
            ValueError: If no email is provided.

        Args:
            email (str): User's email address.
            username (str): User's chosen username.
            password (str): User's password (optional).
            **extra_fields: Additional fields to be included
            in the user instance.

        Returns:
            CustomUser: The created user instance.
        """
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        """
        Create and return a superuser with is_staff and
        is_superuser set to True.

        Args:
            email (str): Superuser's email address.
            username (str): Superuser's username.
            password (str): Superuser's password.
            **extra_fields: Additional fields to be included
            in the user instance.

        Returns:
            CustomUser: The created superuser instance.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, username, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model extending Django's AbstractBaseUser and PermissionsMixin.

    Attributes:
        email (str): The user's unique email address.
        username (str): The user's unique username.
        street (str): The user's street address (optional).
        zip (str): The user's zip/postal code (optional).
        city (str): The user's city (optional).
        is_active (bool): Whether the user's account is active.
        is_staff (bool): Whether the user has staff privileges.
        date_joined (datetime): The date the user joined.
        password_reset_token (UUID): Token for password reset functionality.
    """

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    street = models.CharField(max_length=255, blank=True)
    zip = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    password_reset_token = models.UUIDField(
        default=uuid.uuid4, editable=False, null=True, blank=True
    )

    # Custom user manager
    objects = CustomUserManager()

    # Use email for login instead of username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_user_set',
        related_query_name='custom_user',
    )

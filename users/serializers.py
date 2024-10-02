from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from rest_framework.validators import UniqueValidator

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration. Validates and ensures:
    - Unique email and username.
    - Password and confirmation match.
    - Password meets validation criteria.

    Fields:
        - email (str): User's email, required and unique.
        - username (str): User's chosen username, required and unique.
        - password (str): User's password, required.
        - password2 (str): Confirmation of the password, required.
        - street (str): Optional street address.
        - zip (str): Optional postal code.
        - city (str): Optional city.

    Methods:
        - validate: Ensures password fields match and
        validates password strength.
        - create: Creates a user instance with validated data.
    """
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="This email is already registered."
            )
        ]
    )
    username = serializers.CharField(
        required=True,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="This username is already taken."
            )
        ]
    )
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password',
                  'password2', 'street', 'zip', 'city')
        extra_kwargs = {
            'street': {'required': False},
            'zip': {'required': False},
            'city': {'required': False},
        }

    def validate(self, attrs):
        """
        Ensure that the two password fields match and validate
        password strength.

        Raises:
            serializers.ValidationError: If passwords don't match
            or validation fails.
        """
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password2": "Password fields didn't match."})

        try:
            validate_password(attrs['password'])
        except ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})

        return attrs

    def create(self, validated_data):
        """
        Remove 'password2' from the data and create a new user
        with the validated data.

        Returns:
            User: The newly created user.
        """
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login. Authenticates user based on email and password.

    Fields:
        - email (str): The email of the user.
        - password (str): The password of the user.

    Methods:
        - validate: Authenticates the user and checks if the account is active.
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, data):
        """
        Authenticate the user and ensure the account is active.

        Raises:
            serializers.ValidationError: If authentication fails or
            the account is inactive.
        """
        user = authenticate(email=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError(
                {"non_field_errors": "Invalid email or password."})
        if not user.is_active:
            raise serializers.ValidationError(
                {"non_field_errors": "User account is disabled."})
        data['user'] = user
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile details. Read-only on ID and email.

    Fields:
        - id (int): User's unique ID.
        - email (str): User's email, read-only.
        - username (str): User's username.
        - street (str): User's street address (optional).
        - zip (str): User's postal code (optional).
        - city (str): User's city (optional).
    """
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'street', 'zip', 'city')
        read_only_fields = ('id', 'email')


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer for requesting a password reset. Accepts the user's email.

    Fields:
        - email (str): The email of the user requesting the password reset.
    """
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for confirming password reset with a token and a new password.

    Fields:
        - token (UUID): The reset token to validate.
        - new_password (str): The new password to set for the user.

    Methods:
        - validate_new_password: Ensures the new password meets
        validation requirements.
    """
    token = serializers.UUIDField()
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        """
        Validate the strength of the new password.

        Returns:
            str: The validated password.
        """
        validate_password(value)
        return value

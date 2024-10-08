import uuid
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from .serializers import (
    UserRegistrationSerializer,
    UserProfileSerializer,
    UserLoginSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer
)
from .utils import send_password_reset_email

User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    """
    API view for registering a new user.

    This view allows new users to create an account by providing their email,
    username, and password. Upon successful registration, a JWT access and
    refresh token are returned.

    Methods:
        create: Registers the user and returns authentication tokens.
    """
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        """
        Handle user registration and return JWT tokens if successful.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                "user": UserProfileSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    """
    API view for logging in users.

    This view allows users to authenticate by providing their email
    and password.
    On successful login, a JWT access and refresh token are returned.

    Methods:
        post: Authenticates the user and returns JWT tokens.
    """

    def post(self, request, *args, **kwargs):
        """
        Handle user login and return JWT tokens.
        """
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                "user": UserProfileSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API view for retrieving and updating the user's profile.

    Users can retrieve or update their profile information such as username,
    email, and address.

    Methods:
        get_object: Retrieves the current logged-in user's profile.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Get the currently authenticated user's profile.
        """
        return self.request.user

    def perform_update(self, serializer):
        """
        Update the user's profile and save the changes.
        """
        user = serializer.save()
        user.profile.save()


class UserLogoutView(APIView):
    """
    API view for logging out users.

    This view invalidates the user's refresh token to log them out securely.

    Methods:
        post: Logs out the user by blacklisting the refresh token.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Blacklist the refresh token to log the user out.
        """
        try:
            refresh_token = request.data.get("refresh_token")
            if not refresh_token:
                return Response(
                    {"error": "Refresh token is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"success": "User logged out successfully"},
                status=status.HTTP_200_OK
            )
        except TokenError as e:
            return Response(
                {"error": f"Invalid token: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ChangePasswordView(APIView):
    """
    API view for changing the user's password.

    This view allows authenticated users to update their password by providing
    the current password and a new password.

    Methods:
        post: Changes the user's password.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Handle password change request.
        """
        user = request.user
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')

        if not user.check_password(current_password):
            return Response({'error': 'Current password is incorrect.'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_password(new_password, user)
        except ValidationError as e:
            return Response({'error': e.messages},
                            status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({'message': 'Password changed successfully.'},
                        status=status.HTTP_200_OK)


class PasswordResetRequestView(APIView):
    """
    API view for requesting a password reset.

    This view allows users to request a password reset by providing
    their email.
    An email with a reset token is sent if the user exists.

    Methods:
        post: Sends a password reset email with a unique token.
    """

    def post(self, request):
        """
        Handle password reset request and send email with reset token.
        """
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                reset_token = uuid.uuid4()
                user.password_reset_token = reset_token
                user.save()

                send_password_reset_email(user, reset_token)

                return Response({
                    "message": "Password reset email sent.",
                    "reset_token": str(reset_token)
                }, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({
                    "error": "User with this email does not exist."},
                    status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    """
    API view for confirming a password reset.

    This view allows users to reset their password by providing a valid
    reset token and a new password.

    Methods:
        post: Confirms the password reset by validating the token and setting a
              new password.
    """

    def post(self, request):
        """
        Handle password reset confirmation and update the user's password.
        """
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data['token']
            new_password = serializer.validated_data['new_password']
            try:
                user = User.objects.get(password_reset_token=token)
                user.set_password(new_password)
                user.password_reset_token = None
                user.save()
                return Response({"message": "Password reset successful."},
                                status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({"error": "Invalid token."},
                                status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteAccountView(APIView):
    """
    Delete the authenticated user's account.

    Args:
        request (Request): The HTTP request object containing user information.

    Returns:
        Response: A response indicating successful account deletion
        with HTTP 200 status.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.delete()
        return Response({"message": "Account deleted successfully."},
                        status=status.HTTP_200_OK)

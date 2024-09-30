from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserRegistrationView,
    UserLoginView,
    UserProfileView,
    UserLogoutView,
    ChangePasswordView,
    PasswordResetRequestView,
    PasswordResetConfirmView
)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('change-password/', ChangePasswordView.as_view(),
         name='change-password'),
    path('password-reset-request/', PasswordResetRequestView.as_view(),
         name='password-reset-request'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(),
         name='password-reset-confirm'),
]

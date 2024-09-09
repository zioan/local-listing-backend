from django.urls import path
from .views import ProfileDetailView, PublicProfileView, UserListingsView

urlpatterns = [
    path('profile/', ProfileDetailView.as_view(), name='profile-detail'),
    path('profiles/<str:username>/',
         PublicProfileView.as_view(), name='public-profile'),
    path('listings/user/<str:username>/',
         UserListingsView.as_view(), name='user-listings'),
]

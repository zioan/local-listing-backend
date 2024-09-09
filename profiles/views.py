from rest_framework import generics, permissions
from .models import Profile
from .serializers import ProfileSerializer, PrivateProfileSerializer
from listings.models import Listing
from listings.serializers import ListingSerializer


class ProfileDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = PrivateProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.profile


class PublicProfileView(generics.RetrieveAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    lookup_field = 'user__username'
    lookup_url_kwarg = 'username'


class UserListingsView(generics.ListAPIView):
    serializer_class = ListingSerializer

    def get_queryset(self):
        username = self.kwargs['username']
        return Listing.objects.filter(user__username=username, is_active=True)

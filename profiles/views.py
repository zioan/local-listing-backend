from rest_framework import generics, permissions
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
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

    def retrieve(self, request, *args, **kwargs):
        username = self.kwargs.get('username')
        profile = get_object_or_404(Profile, user__username=username)
        profile.update_listing_counts()
        serializer = self.get_serializer(profile)
        return Response(serializer.data)


class UserListingsView(generics.ListAPIView):
    serializer_class = ListingSerializer

    def get_queryset(self):
        username = self.kwargs['username']
        queryset = Listing.objects.filter(user__username=username)
        active_queryset = queryset.filter(is_active=True)
        return active_queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

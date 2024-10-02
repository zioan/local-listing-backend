from rest_framework import serializers
from .models import Profile
from reviews.serializers import ReviewSerializer


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for the Profile model, exposing public information."""

    username = serializers.CharField(source='user.username', read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    reviews = ReviewSerializer(
        source='user.reviews_received', many=True, read_only=True
    )

    class Meta:
        model = Profile
        fields = [
            'id', 'username', 'bio', 'location', 'date_joined',
            'total_listings', 'active_listings', 'average_rating',
            'reviews'
        ]
        read_only_fields = [
            'id', 'username', 'date_joined', 'total_listings',
            'active_listings', 'average_rating'
        ]


class PrivateProfileSerializer(serializers.ModelSerializer):
    """Serializer for the Profile model, exposing private user information."""

    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Profile
        fields = [
            'id', 'username', 'email', 'bio', 'location', 'date_joined',
            'total_listings', 'active_listings', 'rating', 'num_ratings'
        ]
        read_only_fields = [
            'id', 'username', 'email', 'date_joined',
            'total_listings', 'active_listings', 'rating',
            'num_ratings'
        ]

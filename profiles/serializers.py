from rest_framework import serializers
from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Profile
        fields = ['id', 'username', 'bio', 'location', 'date_joined',
                  'total_listings', 'active_listings', 'rating', 'num_ratings']
        read_only_fields = ['id', 'username', 'date_joined', 'total_listings',
                            'active_listings', 'rating', 'num_ratings']


class PrivateProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Profile
        fields = ['id', 'username', 'email', 'bio', 'location', 'date_joined',
                  'total_listings', 'active_listings', 'rating', 'num_ratings']
        read_only_fields = ['id', 'username', 'email', 'date_joined',
                            'total_listings', 'active_listings', 'rating',
                            'num_ratings']

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Review

User = get_user_model()


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for the Review model."""

    reviewer_username = serializers.SerializerMethodField()
    reviewed_user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'reviewer_username', 'reviewed_user',
                  'rating', 'content', 'created_at']
        read_only_fields = ['reviewer_username', 'reviewed_user', 'created_at']

    def get_reviewer_username(self, obj):
        """Return the username of the reviewer."""
        return obj.reviewer.username if obj.reviewer else None

    def validate(self, data):
        """Validate the review to ensure a user cannot review themselves."""
        request_user = self.context['request'].user

        if 'view' in self.context and hasattr(self.context['view'], 'kwargs'):
            user_id = self.context['view'].kwargs.get('user_id')
            if user_id:
                logged_in_user = User.objects.get(id=user_id)

                if request_user == logged_in_user:
                    raise serializers.ValidationError(
                        "You cannot review yourself."
                    )
        return data

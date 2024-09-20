from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Review

User = get_user_model()


class ReviewSerializer(serializers.ModelSerializer):
    reviewer = serializers.ReadOnlyField(source='reviewer.username')
    reviewed_user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all())

    class Meta:
        model = Review
        fields = ['id', 'reviewer', 'reviewed_user',
                  'rating', 'content', 'created_at']
        read_only_fields = ['reviewer', 'created_at']

    def validate(self, data):
        if self.context['request'].user == data['reviewed_user']:
            raise serializers.ValidationError("You cannot review yourself.")
        return data

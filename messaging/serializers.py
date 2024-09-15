from rest_framework import serializers
from .models import Conversation, Message
from users.serializers import UserProfileSerializer


class MessageSerializer(serializers.ModelSerializer):
    sender = UserProfileSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'content', 'timestamp', 'is_read']


class ConversationSerializer(serializers.ModelSerializer):
    participants = UserProfileSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'participants', 'listing',
                  'created_at', 'updated_at', 'last_message']

    def get_last_message(self, obj):
        last_message = obj.messages.order_by('-timestamp').first()
        return MessageSerializer(last_message).data if last_message else None

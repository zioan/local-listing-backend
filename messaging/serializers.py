from rest_framework import serializers
from .models import Conversation, Message
from listings.models import Listing
from listings.serializers import ListingSerializer
from users.serializers import UserProfileSerializer


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for Message model.

    Represents the details of a message within a conversation.
    """
    sender = UserProfileSerializer(
        read_only=True)  # Sender's profile information

    class Meta:
        model = Message
        fields = ['id', 'sender', 'content', 'timestamp', 'is_read']
        read_only_fields = ['id', 'sender',
                            'timestamp', 'is_read']


class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializer for Conversation model.

    Represents the details of a conversation including its participants
    and listing.
    """
    listing = ListingSerializer(
        read_only=True)
    listing_id = serializers.IntegerField(write_only=True)
    participants = UserProfileSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'listing', 'listing_id', 'participants',
                  'created_at', 'updated_at', 'last_message']
        read_only_fields = ['id', 'participants',
                            'created_at', 'updated_at']

    def create(self, validated_data):
        """Create a new conversation with the associated listing."""
        listing_id = validated_data.pop('listing_id')
        listing = Listing.objects.get(pk=listing_id)
        conversation = Conversation.objects.create(
            listing=listing)
        return conversation

    def to_representation(self, instance):
        """Customize representation of the conversation instance."""
        representation = super().to_representation(instance)
        representation['listing'] = ListingSerializer(
            instance.listing).data
        representation['participants'] = UserProfileSerializer(
            instance.participants.all(), many=True).data
        return representation

    def get_last_message(self, obj):
        """Get the last message in the conversation."""
        last_message = obj.messages.order_by(
            '-timestamp').first()
        # Return serialized message or None
        return MessageSerializer(last_message).data if last_message else None


class ConversationDetailSerializer(ConversationSerializer):
    """
    Serializer for detailed view of Conversation including messages.

    Inherits from ConversationSerializer to add messages.
    """
    messages = MessageSerializer(
        many=True, read_only=True)  # Messages in the conversation

    class Meta(ConversationSerializer.Meta):
        fields = ConversationSerializer.Meta.fields + \
            ['messages']  # Add messages to the fields

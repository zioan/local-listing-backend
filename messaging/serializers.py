from rest_framework import serializers
from .models import Conversation, Message
from listings.models import Listing
from listings.serializers import ListingSerializer
from users.serializers import UserProfileSerializer


class MessageSerializer(serializers.ModelSerializer):
    sender = UserProfileSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'content', 'timestamp', 'is_read']
        read_only_fields = ['id', 'sender', 'timestamp', 'is_read']


class ConversationSerializer(serializers.ModelSerializer):
    listing = ListingSerializer(read_only=True)
    listing_id = serializers.IntegerField(write_only=True)
    participants = UserProfileSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'listing', 'listing_id', 'participants',
                  'created_at', 'updated_at', 'last_message']
        read_only_fields = ['id', 'participants', 'created_at', 'updated_at']

    def create(self, validated_data):
        listing_id = validated_data.pop('listing_id')
        listing = Listing.objects.get(pk=listing_id)
        conversation = Conversation.objects.create(listing=listing)
        return conversation

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['listing'] = ListingSerializer(instance.listing).data
        representation['participants'] = UserProfileSerializer(
            instance.participants.all(), many=True).data
        return representation

    def get_last_message(self, obj):
        last_message = obj.messages.order_by('-timestamp').first()
        return MessageSerializer(last_message).data if last_message else None


class ConversationDetailSerializer(ConversationSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta(ConversationSerializer.Meta):
        fields = ConversationSerializer.Meta.fields + ['messages']

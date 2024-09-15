from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from listings.models import Listing
from rest_framework import serializers


class ConversationListCreate(generics.ListCreateAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Conversation.objects.filter(participants=self.request.user)
        listing_id = self.request.query_params.get('listing', None)
        if listing_id is not None:
            queryset = queryset.filter(listing_id=listing_id)
        return queryset

    def perform_create(self, serializer):
        try:
            listing_id = self.request.data.get('listing')
            listing = Listing.objects.get(pk=listing_id)

            # Debugging logs
            print(
                f"Attempting to create conversation for listing {listing_id}")
            print(f"Current user: {self.request.user}")
            print(f"Listing owner: {listing.user}")

            # Check if conversation already exists
            existing_conversation = Conversation.objects.filter(
                participants=self.request.user,
                listing=listing
            ).first()

            if existing_conversation:
                print(
                    f"Existing conversation found: {existing_conversation.id}")
                return existing_conversation

            # Prevent messaging self
            if self.request.user == listing.user:
                raise serializers.ValidationError(
                    "Cannot start a conversation with yourself")

            conversation = serializer.save(listing=listing)
            conversation.participants.add(self.request.user, listing.user)
            print(f"New conversation created: {conversation.id}")
            return conversation

        except Listing.DoesNotExist:
            raise serializers.ValidationError("Invalid listing ID")
        except Exception as e:
            print(f"Error creating conversation: {str(e)}")
            raise serializers.ValidationError(str(e))

    def create(self, request, *args, **kwargs):
        try:
            conversation = self.perform_create(
                self.get_serializer(data=request.data))
            serializer = self.get_serializer(conversation)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except serializers.ValidationError as e:
            return Response({'error': str(e)},
                            status=status.HTTP_400_BAD_REQUEST)


class MessageListCreate(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        conversation_id = self.kwargs['conversation_id']
        return Message.objects.filter(conversation_id=conversation_id)

    def perform_create(self, serializer):
        conversation_id = self.kwargs['conversation_id']
        conversation = Conversation.objects.get(pk=conversation_id)
        serializer.save(sender=self.request.user, conversation=conversation)


class UnreadMessageCount(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        unread_count = Message.objects.filter(
            conversation__participants=request.user,
            is_read=False
        ).exclude(sender=request.user).count()
        return Response({'unread_count': unread_count})

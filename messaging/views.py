from rest_framework import generics, permissions, status, serializers
from django.db.models import Count
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Conversation, Message
from .serializers import (
    ConversationSerializer,
    ConversationDetailSerializer,
    MessageSerializer
)
from listings.models import Listing


class ConversationListCreate(generics.ListCreateAPIView):
    """
    API view to list and create conversations.

    Users can start conversations related to listings they are not selling.
    """
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter conversations by listing ID or return all conversations."""
        user = self.request.user
        listing_id = self.request.query_params.get('listing', None)
        if listing_id:
            listing = get_object_or_404(Listing, pk=listing_id)
            return Conversation.objects.filter(listing=listing,
                                               participants=user)
        else:
            return Conversation.objects.filter(participants=user)

    def list(self, request, *args, **kwargs):
        """Return a list of conversations."""
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @transaction.atomic
    def perform_create(self, serializer):
        """Create a new conversation if it doesn't already exist."""
        listing_id = serializer.validated_data['listing_id']
        listing = get_object_or_404(Listing, pk=listing_id)
        if self.request.user == listing.user:
            raise serializers.ValidationError(
                "Cannot start a conversation with yourself")

        existing_conversation = Conversation.objects.filter(
            participants=self.request.user, listing=listing
        ).first()

        # Return existing conversation if found
        if existing_conversation:
            return existing_conversation

        # Create and associate new conversation
        conversation = serializer.save(listing=listing)
        conversation.participants.add(self.request.user, listing.user)
        return conversation

    def create(self, request, *args, **kwargs):
        """Handle the creation of a conversation."""
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors,
                                status=status.HTTP_400_BAD_REQUEST)

            conversation = self.perform_create(serializer)
            serializer = self.get_serializer(conversation)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except serializers.ValidationError as e:
            return Response({'error': str(e)},
                            status=status.HTTP_400_BAD_REQUEST)
        except Listing.DoesNotExist:
            return Response({"error": "Listing not found"},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ConversationDetail(generics.RetrieveAPIView):
    """
    API view to retrieve a specific conversation.

    Accessible only to participants of the conversation.
    """
    serializer_class = ConversationDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return conversations for the authenticated user."""
        return Conversation.objects.filter(participants=self.request.user)


class MessageListCreate(generics.ListCreateAPIView):
    """
    API view to list and create messages within a conversation.

    Accessible only to participants of the conversation.
    """
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return messages for a specific conversation."""
        conversation_id = self.kwargs['conversation_id']
        conversation = get_object_or_404(Conversation, pk=conversation_id)

        if self.request.user not in conversation.participants.all():
            return Message.objects.none()
        return Message.objects.filter(conversation_id=conversation_id)

    def perform_create(self, serializer):
        """Create a new message associated with the conversation."""
        conversation_id = self.kwargs['conversation_id']
        conversation = get_object_or_404(Conversation, pk=conversation_id)

        if self.request.user not in conversation.participants.all():
            raise permissions.PermissionDenied(
                "You are not a participant in this conversation.")

        serializer.save(sender=self.request.user, conversation=conversation)


class ListingIncomingMessages(generics.ListAPIView):
    """
    API view to list incoming messages for a specific listing.

    Returns conversations related to the listing for the user.
    """
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return conversations related to the specified listing."""
        listing_id = self.kwargs['listing_id']
        listing = get_object_or_404(Listing, pk=listing_id)
        user = self.request.user

        if user == listing.user:
            return Conversation.objects.filter(listing=listing)
        else:
            return Conversation.objects.filter(listing=listing,
                                               participants=user)

    def list(self, request, *args, **kwargs):
        """Return a list of conversations related to the listing."""
        try:
            queryset = self.get_queryset()
            if not queryset.exists():
                id = self.kwargs['listing_id']
                if Listing.objects.filter(pk=id).exists():
                    return Response({"message": "No conversations found."},
                                    status=status.HTTP_200_OK)
                else:
                    return Response({"error": "Listing not found."},
                                    status=status.HTTP_404_NOT_FOUND)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except PermissionDenied as e:
            return Response({"error": str(e)},
                            status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({"error": f"Unexpected error occurred: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UnreadMessageCount(generics.GenericAPIView):
    """
    API view to get the count of unread messages for the authenticated user.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Return the count of unread messages."""
        unread_count = Message.objects.filter(
            conversation__participants=request.user, is_read=False
        ).exclude(sender=request.user).count()
        return Response({'unread_count': unread_count})


class MarkMessagesAsRead(generics.GenericAPIView):
    """
    API view to mark messages as read in a conversation.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, conversation_id):
        """Mark specified messages in a conversation as read."""
        conversation = get_object_or_404(Conversation, id=conversation_id)

        if request.user not in conversation.participants.all():
            raise PermissionDenied(
                "You are not a participant in this conversation.")

        message_ids = request.data.get('message_ids', [])
        messages = Message.objects.filter(
            id__in=message_ids,
            conversation=conversation,
            is_read=False
        ).exclude(sender=request.user)

        messages.update(is_read=True)
        return Response({"status": "Messages marked as read"},
                        status=status.HTTP_200_OK)


class ConversationUnreadCounts(generics.GenericAPIView):
    """
    API view to get unread message counts grouped by conversation.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Return unread message counts for each conversation."""
        unread_counts = (
            Message.objects.filter(
                conversation__participants=request.user, is_read=False
            )
            .exclude(sender=request.user)
            .values('conversation')
            .annotate(unread_count=Count('id'))
        )

        unread_dict = {item['conversation']: item['unread_count']
                       for item in unread_counts}
        return Response(unread_dict)

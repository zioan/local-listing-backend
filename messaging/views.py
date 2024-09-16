from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Conversation, Message
from .serializers import (
    ConversationSerializer,
    ConversationDetailSerializer,
    MessageSerializer)
from listings.models import Listing
import logging

logger = logging.getLogger(__name__)


class ConversationListCreate(generics.ListCreateAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        listing_id = self.request.query_params.get('listing', None)

        if listing_id:
            listing = get_object_or_404(Listing, pk=listing_id)
            return Conversation.objects.filter(listing=listing,
                                               participants=user)
        else:
            return Conversation.objects.filter(participants=user)

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error in ConversationListCreate.list: {str(e)}")
            return Response({"error": "Wrror occurred while fetching conversations."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @transaction.atomic
    def perform_create(self, serializer):
        listing_id = serializer.validated_data['listing_id']
        listing = get_object_or_404(Listing, pk=listing_id)

        if self.request.user == listing.user:
            raise serializers.ValidationError(
                "Cannot start a conversation with yourself")

        existing_conversation = Conversation.objects.filter(
            participants=self.request.user,
            listing=listing
        ).first()

        if existing_conversation:
            return existing_conversation

        conversation = serializer.save(listing=listing)
        conversation.participants.add(self.request.user, listing.user)
        return conversation

    def create(self, request, *args, **kwargs):
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
            logger.error(f"Error in ConversationListCreate.create: {str(e)}")
            return Response({"error": "Error occurred while creating the conversation."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ConversationDetail(generics.RetrieveAPIView):
    serializer_class = ConversationDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(participants=self.request.user)


class MessageListCreate(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        conversation_id = self.kwargs['conversation_id']
        conversation = get_object_or_404(Conversation, pk=conversation_id)
        if self.request.user not in conversation.participants.all():
            raise PermissionDenied(
                "You are not a participant in this conversation.")
        return Message.objects.filter(conversation_id=conversation_id)

    def perform_create(self, serializer):
        conversation_id = self.kwargs['conversation_id']
        conversation = get_object_or_404(Conversation, pk=conversation_id)
        if self.request.user not in conversation.participants.all():
            raise PermissionDenied(
                "You are not a participant in this conversation.")
        serializer.save(sender=self.request.user, conversation=conversation)


class ListingIncomingMessages(generics.ListAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        listing_id = self.kwargs['listing_id']
        listing = get_object_or_404(Listing, pk=listing_id)
        user = self.request.user

        # Check if the user is either the listing owner or a participant in a conversation for this listing
        if user == listing.user:
            # If the user is the listing owner, return all conversations for this listing
            return Conversation.objects.filter(listing=listing)
        else:
            # If the user is a potential buyer, return only their conversations for this listing
            return Conversation.objects.filter(listing=listing,
                                               participants=user)

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            if not queryset.exists():
                if Listing.objects.filter(pk=self.kwargs['listing_id']).exists():
                    return Response({"message": "No conversations found for this listing."}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "Listing not found."}, status=status.HTTP_404_NOT_FOUND)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except PermissionDenied as e:
            return Response({"error": str(e)},
                            status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            logger.error(f"Error in ListingIncomingMessages: {str(e)}")
            return Response({"error": "An unexpected error occurred."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UnreadMessageCount(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        unread_count = Message.objects.filter(
            conversation__participants=request.user,
            is_read=False
        ).exclude(sender=request.user).count()
        return Response({'unread_count': unread_count})

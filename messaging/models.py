from django.db import models
from django.conf import settings
from listings.models import Listing


class Conversation(models.Model):
    """
    Represents a conversation related to a specific listing.

    Participants can be multiple users, and the conversation is tied
    to a listing.
    """
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='conversations'
    )
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name='conversations'
    )
    created_at = models.DateTimeField(
        auto_now_add=True)
    updated_at = models.DateTimeField(
        auto_now=True)

    class Meta:
        # Ensure only one conversation per listing
        unique_together = ['listing']


class Message(models.Model):
    """
    Represents a message sent within a conversation.

    Each message is associated with a conversation and has a sender.
    """
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']  # Order messages by timestamp

from django.contrib import admin
from .models import Conversation, Message


class MessageInline(admin.TabularInline):
    """
    Inline admin class for displaying messages within a conversation.
    """
    model = Message
    extra = 0  # No extra empty forms
    readonly_fields = ('sender', 'content', 'timestamp', 'is_read')


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    """
    Admin view for managing conversations.

    Displays a list of conversations and allows inlining of messages.
    """
    list_display = ('id', 'listing', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('listing__title', 'participants__username')
    filter_horizontal = ('participants',)
    inlines = [MessageInline]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """
    Admin view for managing messages within conversations.

    Displays a list of messages and allows filtering and searching.
    """
    list_display = ('id', 'conversation', 'sender',
                    'content', 'timestamp', 'is_read')
    list_filter = ('is_read', 'timestamp')
    search_fields = ('content', 'sender__username',
                     'conversation__listing__title')
    readonly_fields = ('conversation', 'sender', 'timestamp')

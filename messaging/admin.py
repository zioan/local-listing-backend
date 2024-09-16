from django.contrib import admin
from .models import Conversation, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ('sender', 'content', 'timestamp', 'is_read')


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'listing', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('listing__title', 'participants__username')
    filter_horizontal = ('participants',)
    inlines = [MessageInline]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'sender',
                    'content', 'timestamp', 'is_read')
    list_filter = ('is_read', 'timestamp')
    search_fields = ('content', 'sender__username',
                     'conversation__listing__title')
    readonly_fields = ('conversation', 'sender', 'timestamp')

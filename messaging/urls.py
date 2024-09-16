from django.urls import path
from . import views

urlpatterns = [
    path('conversations/', views.ConversationListCreate.as_view(),
         name='conversation-list-create'),
    path('conversations/<int:conversation_id>/messages/',
         views.MessageListCreate.as_view(), name='message-list-create'),
    path('conversations/<int:conversation_id>/mark-as-read/',
         views.MarkMessagesAsRead.as_view(), name='mark-messages-as-read'),
    path('conversation-unread-counts/',
         views.ConversationUnreadCounts.as_view(),
         name='conversation-unread-counts'),
    path('unread-messages/', views.UnreadMessageCount.as_view(),
         name='unread-message-count'),
    path('listing/<int:listing_id>/messages/',
         views.ListingIncomingMessages.as_view(),
         name='listing-incoming-messages'),
]

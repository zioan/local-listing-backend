from django.urls import path
from . import views

urlpatterns = [
    path('conversations/', views.ConversationListCreate.as_view(),
         name='conversation-list-create'),
    path('conversations/<int:conversation_id>/messages/',
         views.MessageListCreate.as_view(), name='message-list-create'),
    path('unread-messages/', views.UnreadMessageCount.as_view(),
         name='unread-message-count'),
]

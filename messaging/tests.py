from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import Conversation, Message
from listings.models import Listing, Category, Subcategory
from .serializers import ConversationSerializer, MessageSerializer

User = get_user_model()


class MessagingModelTests(TestCase):
    """
    Test case for the Messaging models (Conversation and Message).
    """

    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1', email='user1@example.com', password='pass1234')
        self.user2 = User.objects.create_user(
            username='user2', email='user2@example.com', password='pass1234')
        self.category = Category.objects.create(name='Electronics')
        self.subcategory = Subcategory.objects.create(
            name='Phones', category=self.category)
        self.listing = Listing.objects.create(
            title='iPhone',
            description='A great iPhone',
            user=self.user1,
            category=self.category,
            subcategory=self.subcategory,
            price=500
        )
        self.conversation = Conversation.objects.create(listing=self.listing)
        self.conversation.participants.add(self.user1, self.user2)

    def test_conversation_creation(self):
        """
        Test the creation of a Conversation instance and its relationships.
        """
        self.assertEqual(self.conversation.listing, self.listing)
        self.assertEqual(self.conversation.participants.count(), 2)
        self.assertIn(self.user1, self.conversation.participants.all())
        self.assertIn(self.user2, self.conversation.participants.all())

    def test_message_creation(self):
        """
        Test the creation of a Message instance and its relationships.
        """
        message = Message.objects.create(
            conversation=self.conversation,
            sender=self.user1,
            content='Hello, is this still available?'
        )
        self.assertEqual(message.conversation, self.conversation)
        self.assertEqual(message.sender, self.user1)
        self.assertEqual(message.content, 'Hello, is this still available?')
        self.assertFalse(message.is_read)


class MessagingSerializerTests(TestCase):
    """
    Test case for the Messaging serializers
    (ConversationSerializer and MessageSerializer).
    """

    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1', email='user1@example.com', password='pass1234')
        self.user2 = User.objects.create_user(
            username='user2', email='user2@example.com', password='pass1234')
        self.category = Category.objects.create(name='Electronics')
        self.subcategory = Subcategory.objects.create(
            name='Phones', category=self.category)
        self.listing = Listing.objects.create(
            title='iPhone',
            description='A great iPhone',
            user=self.user1,
            category=self.category,
            subcategory=self.subcategory,
            price=500
        )
        self.conversation = Conversation.objects.create(listing=self.listing)
        self.conversation.participants.add(self.user1, self.user2)
        self.message = Message.objects.create(
            conversation=self.conversation,
            sender=self.user1,
            content='Hello, is this still available?'
        )

    def test_conversation_serializer(self):
        """
        Test the ConversationSerializer output structure and content.
        """
        serializer = ConversationSerializer(instance=self.conversation)
        data = serializer.data
        expected_fields = set(
            ['id', 'listing', 'participants', 'created_at',
             'updated_at', 'last_message'])
        self.assertEqual(set(data.keys()), expected_fields)
        self.assertEqual(data['listing']['title'], 'iPhone')

    def test_message_serializer(self):
        """
        Test the MessageSerializer output structure and content.
        """
        serializer = MessageSerializer(instance=self.message)
        data = serializer.data
        self.assertEqual(set(data.keys()), set(
            ['id', 'sender', 'content', 'timestamp', 'is_read']))
        self.assertEqual(data['content'], 'Hello, is this still available?')


class MessagingViewTests(TestCase):
    """
    Test case for the Messaging views and API endpoints.
    """

    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            username='user1', email='user1@example.com', password='pass1234')
        self.user2 = User.objects.create_user(
            username='user2', email='user2@example.com', password='pass1234')
        self.category = Category.objects.create(name='Electronics')
        self.subcategory = Subcategory.objects.create(
            name='Phones', category=self.category)
        self.listing = Listing.objects.create(
            title='iPhone',
            description='A great iPhone',
            user=self.user1,
            category=self.category,
            subcategory=self.subcategory,
            price=500
        )
        self.conversation = Conversation.objects.create(listing=self.listing)
        self.conversation.participants.add(self.user1, self.user2)
        self.message = Message.objects.create(
            conversation=self.conversation,
            sender=self.user1,
            content='Hello, is this still available?'
        )

    def test_conversation_list_create(self):
        """
        Test the GET and POST methods of the ConversationListCreate view.
        """
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(reverse('conversation-list-create'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        new_listing = Listing.objects.create(
            title='MacBook',
            description='A great MacBook',
            user=self.user1,
            category=self.category,
            subcategory=self.subcategory,
            price=1000
        )
        response = self.client.post(
            reverse('conversation-list-create'),
            {'listing_id': new_listing.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_message_list_create(self):
        """
        Test the GET and POST methods of the MessageListCreate view.
        """
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(reverse(
            'message-list-create',
            kwargs={'conversation_id': self.conversation.id}
        ))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        response = self.client.post(reverse('message-list-create', kwargs={
                                    'conversation_id': self.conversation.id}),
                                    {'content': 'Yes, it is!'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Message.objects.count(), 2)

    def test_mark_messages_as_read(self):
        """
        Test the functionality to mark messages as read.
        """
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(reverse('mark-messages-as-read', kwargs={
                                    'conversation_id': self.conversation.id}),
                                    {'message_ids': [self.message.id]})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.message.refresh_from_db()
        self.assertTrue(self.message.is_read)

    def test_unread_message_count(self):
        """
        Test the API endpoint that returns the count of unread messages.
        """

        self.client.force_authenticate(user=self.user2)
        response = self.client.get(reverse('unread-message-count'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['unread_count'], 1)

    def test_conversation_unread_counts(self):
        """
        Test the API endpoint that returns unread message counts
        for conversations.
        """
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(reverse('conversation-unread-counts'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        conversation_id = self.conversation.id
        self.assertIn(conversation_id, response.data)
        self.assertEqual(response.data[conversation_id], 1)

    def test_listing_incoming_messages(self):
        """
        Test the API endpoint that returns incoming messages for
        a specific listing.
        """
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(
            reverse('listing-incoming-messages',
                    kwargs={'listing_id': self.listing.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

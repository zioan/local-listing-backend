from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import Profile
from .serializers import ProfileSerializer, PrivateProfileSerializer

User = get_user_model()


class ProfileModelTests(TestCase):
    """
    Test cases for the Profile model.
    """

    def setUp(self):
        """
        Set up test data.
        """
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass123'
        )
        self.profile = self.user.profile

    def test_profile_creation(self):
        """
        Test that a profile is created automatically when a user is created.
        """
        self.assertIsInstance(self.profile, Profile)
        self.assertEqual(self.profile.user, self.user)

    def test_profile_str_representation(self):
        """
        Test the string representation of a Profile instance.
        """
        expected_str = f"{self.user.username}'s profile"
        self.assertEqual(str(self.profile), expected_str)

    def test_update_listing_counts(self):
        """
        Test the update_listing_counts method of the Profile model.
        """
        self.user.listings.create(title="Test Listing 1", is_active=True)
        self.user.listings.create(title="Test Listing 2", is_active=False)

        self.profile.update_listing_counts()
        self.assertEqual(self.profile.total_listings, 2)
        self.assertEqual(self.profile.active_listings, 2)


class ProfileViewTests(TestCase):
    """
    Test cases for the Profile views.
    """

    def setUp(self):
        """
        Set up test data and API client.
        """
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass123'
        )
        self.profile = self.user.profile

    def test_profile_detail_view(self):
        """
        Test the ProfileDetailView for authenticated users.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/profiles/profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)

    def test_public_profile_view(self):
        """
        Test the PublicProfileView.
        """
        response = self.client.get(
            f'/api/profiles/profiles/{self.user.username}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)

    def test_user_listings_view(self):
        """
        Test the UserListingsView.
        """
        self.user.listings.create(title="Test Listing 1", is_active=True)
        self.user.listings.create(title="Test Listing 2", is_active=True)
        self.user.listings.create(title="Test Listing 3", is_active=False)

        response = self.client.get(
            f'/api/profiles/listings/user/{self.user.username}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)


class ProfileSerializerTests(TestCase):
    """
    Test cases for the Profile serializers.
    """

    def setUp(self):
        """
        Set up test data.
        """
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass123'
        )
        self.profile = self.user.profile

    def test_profile_serializer(self):
        """
        Test the ProfileSerializer.
        """
        serializer = ProfileSerializer(instance=self.profile)
        self.assertEqual(serializer.data['username'], self.user.username)
        self.assertIn('average_rating', serializer.data)
        self.assertIn('reviews', serializer.data)

    def test_private_profile_serializer(self):
        """
        Test the PrivateProfileSerializer.
        """
        serializer = PrivateProfileSerializer(instance=self.profile)
        self.assertEqual(serializer.data['username'], self.user.username)
        self.assertEqual(serializer.data['email'], self.user.email)
        self.assertIn('bio', serializer.data)
        self.assertIn('location', serializer.data)

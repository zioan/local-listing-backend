from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserProfileSerializer

User = get_user_model()


class UserModelTests(TestCase):
    """
    Test cases for the CustomUser model.
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

    def test_user_creation(self):
        """
        Test that a user can be created with the correct attributes.
        """
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'testuser@example.com')
        self.assertTrue(self.user.check_password('testpass123'))

    def test_user_str_representation(self):
        """
        Test the string representation of a CustomUser instance.
        """
        expected_str = 'testuser@example.com'
        self.assertEqual(str(self.user), expected_str)


class UserViewTests(TestCase):
    """
    Test cases for the User views.
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
        self.client.force_authenticate(user=self.user)

    def test_user_registration(self):
        """
        Test registering a new user.
        """
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'password2': 'newpass123'
        }
        response = self.client.post('/api/users/register/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)

    def test_user_profile_retrieval(self):
        """
        Test retrieving the authenticated user's profile.
        """
        response = self.client.get('/api/users/profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)

    def test_user_profile_update(self):
        """
        Test updating the authenticated user's profile.
        """
        data = {
            'username': 'updateduser',
            'street': '123 Main St',
            'zip': '12345',
            'city': 'Anytown'
        }
        response = self.client.put('/api/users/profile/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'updateduser')
        self.assertEqual(self.user.street, '123 Main St')

    def test_user_logout(self):
        """
        Test logging out the user.
        """
        # Authenticate the user by manually creating a token
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)

        # Set the Authorization header to simulate login
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        # Log out the user by blacklisting the refresh token
        response = self.client.post(
            '/api/users/logout/', {'refresh_token': str(refresh)})

        # Ensure logout is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'],
                         'User logged out successfully')

    def test_change_password(self):
        """
        Test changing the user's password.
        """
        data = {
            'current_password': 'testpass123',
            'new_password': 'newpass123'
        }
        response = self.client.post('/api/users/change-password/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.check_password('newpass123'))


class UserSerializerTests(TestCase):
    """
    Test cases for the User serializer.
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
        self.serializer = UserProfileSerializer(instance=self.user)

    def test_user_serializer_contains_expected_fields(self):
        """
        Test that the UserProfileSerializer contains the expected fields.
        """
        data = self.serializer.data
        self.assertCountEqual(
            data.keys(), ['id', 'email', 'username', 'street', 'zip', 'city'])

    def test_user_serializer_content(self):
        """
        Test that the UserProfileSerializer correctly serializes
        the User instance.
        """
        data = self.serializer.data
        self.assertEqual(data['email'], self.user.email)
        self.assertEqual(data['username'], self.user.username)

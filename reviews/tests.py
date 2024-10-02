from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import Review
from .serializers import ReviewSerializer

User = get_user_model()


class ReviewModelTests(TestCase):
    """
    Test cases for the Review model.
    """

    def setUp(self):
        """
        Set up test data.
        """
        self.reviewer = User.objects.create_user(
            username='reviewer',
            email='reviewer@example.com',
            password='testpass123'
        )
        self.reviewed_user = User.objects.create_user(
            username='reviewed',
            email='reviewed@example.com',
            password='testpass123'
        )
        self.review = Review.objects.create(
            reviewer=self.reviewer,
            reviewed_user=self.reviewed_user,
            rating=4,
            content="Great user!"
        )

    def test_review_creation(self):
        """
        Test that a review can be created with the correct attributes.
        """
        self.assertEqual(self.review.reviewer, self.reviewer)
        self.assertEqual(self.review.reviewed_user, self.reviewed_user)
        self.assertEqual(self.review.rating, 4)
        self.assertEqual(self.review.content, "Great user!")

    def test_review_str_representation(self):
        """
        Test the string representation of a Review instance.
        """
        reviewer = self.reviewer.username
        reviewed = self.reviewed_user.username
        expected_str = f"Review by {reviewer} for {reviewed}"
        self.assertEqual(str(self.review), expected_str)


class ReviewViewTests(TestCase):
    """
    Test cases for the Review views.
    """

    def setUp(self):
        """
        Set up test data and API client.
        """
        self.client = APIClient()
        self.reviewer = User.objects.create_user(
            username='reviewer',
            email='reviewer@example.com',
            password='testpass123'
        )
        self.reviewed_user = User.objects.create_user(
            username='reviewed',
            email='reviewed@example.com',
            password='testpass123'
        )

    def test_create_review(self):
        """
        Test creating a new review.
        """
        self.client.force_authenticate(user=self.reviewer)
        data = {
            'rating': 5,
            'content': 'Excellent user!'
        }
        response = self.client.post(
            f'/api/reviews/users/{self.reviewed_user.id}/reviews/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(Review.objects.get().content, 'Excellent user!')

    def test_list_reviews(self):
        """
        Test listing reviews for a user.
        """
        Review.objects.create(
            reviewer=self.reviewer, reviewed_user=self.reviewed_user,
            rating=4, content="Good user!")

        # Ensure the client is authenticated
        self.client.force_authenticate(user=self.reviewer)

        response = self.client.get(
            f'/api/reviews/users/{self.reviewed_user.id}/reviews/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_update_review(self):
        """
        Test updating an existing review.
        """
        review = Review.objects.create(
            reviewer=self.reviewer, reviewed_user=self.reviewed_user,
            rating=3, content="Average user")
        self.client.force_authenticate(user=self.reviewer)
        data = {
            'rating': 4,
            'content': 'Better than average user'
        }
        response = self.client.put(f'/api/reviews/reviews/{review.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Review.objects.get().content,
                         'Better than average user')

    def test_delete_review(self):
        """
        Test deleting a review.
        """
        review = Review.objects.create(
            reviewer=self.reviewer, reviewed_user=self.reviewed_user,
            rating=2, content="Not great")
        self.client.force_authenticate(user=self.reviewer)
        response = self.client.delete(f'/api/reviews/reviews/{review.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Review.objects.count(), 0)


class ReviewSerializerTests(TestCase):
    """
    Test cases for the Review serializer.
    """

    def setUp(self):
        """
        Set up test data.
        """
        self.reviewer = User.objects.create_user(
            username='reviewer',
            email='reviewer@example.com',
            password='testpass123'
        )
        self.reviewed_user = User.objects.create_user(
            username='reviewed',
            email='reviewed@example.com',
            password='testpass123'
        )
        self.review_data = {
            'reviewer': self.reviewer,
            'reviewed_user': self.reviewed_user,
            'rating': 5,
            'content': 'Fantastic user!'
        }
        self.review = Review.objects.create(**self.review_data)
        self.serializer = ReviewSerializer(instance=self.review)

    def test_review_serializer_contains_expected_fields(self):
        """
        Test that the ReviewSerializer contains the expected fields.
        """
        data = self.serializer.data
        self.assertCountEqual(data.keys(), [
                              'id', 'reviewer_username', 'reviewed_user',
                              'rating', 'content', 'created_at'])

    def test_review_serializer_content(self):
        """
        Test that the ReviewSerializer correctly serializes
        the Review instance.
        """
        data = self.serializer.data
        self.assertEqual(data['reviewer_username'], self.reviewer.username)
        self.assertEqual(data['reviewed_user'], self.reviewed_user.id)
        self.assertEqual(data['rating'], 5)
        self.assertEqual(data['content'], 'Fantastic user!')

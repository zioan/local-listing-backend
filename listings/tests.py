from django.test import TestCase
import os
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import Category, Subcategory, Listing
from .serializers import (
    CategorySerializer,
    SubcategorySerializer,
    ListingSerializer
)

test_static_root = os.path.join(settings.BASE_DIR, 'test_static')
os.makedirs(test_static_root, exist_ok=True)

User = get_user_model()


class CategoryModelTest(TestCase):
    """
    Test case for the Category model.
    """

    def setUp(self):
        self.category = Category.objects.create(name="Electronics")

    def test_category_creation(self):
        """
        Test the creation of a Category instance and its string representation.
        """
        self.assertEqual(self.category.name, "Electronics")
        self.assertTrue(isinstance(self.category, Category))
        self.assertEqual(str(self.category), "Electronics")


class SubcategoryModelTest(TestCase):
    """
    Test case for the Subcategory model.
    """

    def setUp(self):
        self.category = Category.objects.create(name="Electronics")
        self.subcategory = Subcategory.objects.create(
            name="Smartphones", category=self.category)

    def test_subcategory_creation(self):
        """
        Test the creation of a Subcategory instance and its relationships.
        """
        self.assertEqual(self.subcategory.name, "Smartphones")
        self.assertEqual(self.subcategory.category, self.category)
        self.assertTrue(isinstance(self.subcategory, Subcategory))
        self.assertEqual(str(self.subcategory), "Electronics - Smartphones")


class ListingModelTest(TestCase):
    """
    Test case for the Listing model.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com",
            password="testpass123")
        self.category = Category.objects.create(name="Electronics")
        self.subcategory = Subcategory.objects.create(
            name="Smartphones", category=self.category)
        self.listing = Listing.objects.create(
            title="iPhone 12",
            description="Brand new iPhone 12",
            user=self.user,
            category=self.category,
            subcategory=self.subcategory,
            price=799.99,
            condition="new"
        )

    def test_listing_creation(self):
        """
        Test the creation of a Listing instance and its relationships.
        """
        self.assertEqual(self.listing.title, "iPhone 12")
        self.assertEqual(self.listing.user, self.user)
        self.assertEqual(self.listing.category, self.category)
        self.assertEqual(self.listing.subcategory, self.subcategory)
        self.assertEqual(self.listing.price, 799.99)
        self.assertEqual(self.listing.condition, "new")
        self.assertTrue(isinstance(self.listing, Listing))
        self.assertEqual(str(self.listing), "iPhone 12")


class CategorySerializerTest(TestCase):
    """
    Test case for the CategorySerializer.
    """

    def setUp(self):
        self.category_attributes = {
            'name': 'Electronics'
        }
        self.category = Category.objects.create(**self.category_attributes)
        self.serializer = CategorySerializer(instance=self.category)

    def test_contains_expected_fields(self):
        """
        Test that the serialized data contains the expected fields.
        """
        data = self.serializer.data
        self.assertEqual(set(data.keys()), set(['id', 'name']))


class SubcategorySerializerTest(TestCase):
    """
    Test case for the SubcategorySerializer.
    """

    def setUp(self):
        self.category = Category.objects.create(name='Electronics')
        self.subcategory_attributes = {
            'name': 'Smartphones',
            'category': self.category
        }
        self.subcategory = Subcategory.objects.create(
            **self.subcategory_attributes)
        self.serializer = SubcategorySerializer(instance=self.subcategory)

    def test_contains_expected_fields(self):
        """
        Test that the serialized data contains the expected fields.
        """
        data = self.serializer.data
        self.assertEqual(set(data.keys()), set(['id', 'name', 'category']))


class ListingSerializerTest(TestCase):
    """
    Test case for the ListingSerializer.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com",
            password="testpass123")
        self.category = Category.objects.create(name="Electronics")
        self.subcategory = Subcategory.objects.create(
            name="Smartphones", category=self.category)
        self.listing_attributes = {
            'title': 'iPhone 12',
            'description': 'Brand new iPhone 12',
            'user': self.user,
            'category': self.category,
            'subcategory': self.subcategory,
            'price': 799.99,
            'condition': 'new'
        }
        self.listing = Listing.objects.create(**self.listing_attributes)
        self.serializer = ListingSerializer(instance=self.listing)

    def test_contains_expected_fields(self):
        """
        Test that the serialized data contains the expected fields.
        """
        data = self.serializer.data
        expected_fields = set([
            'id', 'title', 'description', 'user', 'listing_type', 'category',
            'category_name', 'subcategory', 'subcategory_name', 'price',
            'price_type', 'condition', 'delivery_option', 'location',
            'event_date', 'created_at', 'updated_at', 'is_active', 'status',
            'view_count', 'favorite_count', 'images', 'is_favorited',
            'has_conversation'
        ])
        self.assertEqual(set(data.keys()), expected_fields)


class ListingViewSetTest(TestCase):
    """
    Test case for the ListingViewSet.
    """

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com",
            password="testpass123")
        self.category = Category.objects.create(name="Electronics")
        self.subcategory = Subcategory.objects.create(
            name="Smartphones", category=self.category)
        self.listing = Listing.objects.create(
            title="iPhone 12",
            description="Brand new iPhone 12",
            user=self.user,
            category=self.category,
            subcategory=self.subcategory,
            price=799.99,
            condition="new"
        )
        self.valid_payload = {
            'title': 'Samsung Galaxy S21',
            'description': 'Brand new Samsung Galaxy S21',
            'category': self.category.id,
            'subcategory': self.subcategory.id,
            'price': 899.99,
            'condition': 'new'
        }
        self.invalid_payload = {
            'title': '',
            'description': 'Invalid listing',
            'category': self.category.id,
            'subcategory': self.subcategory.id,
            'price': 'invalid',
            'condition': 'invalid'
        }

    def test_create_valid_listing(self):
        """
        Test creating a new listing with valid data.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            reverse('listing-list'),
            data=self.valid_payload
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invalid_listing(self):
        """
        Test creating a new listing with invalid data.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            reverse('listing-list'),
            data=self.invalid_payload
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_listing(self):
        """
        Test retrieving a specific listing.
        """
        response = self.client.get(
            reverse('listing-detail', kwargs={'pk': self.listing.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        listing = Listing.objects.get(pk=self.listing.pk)
        serializer = ListingSerializer(listing)
        self.assertEqual(response.data, serializer.data)

    def test_update_listing(self):
        """
        Test updating an existing listing.
        """
        self.client.force_authenticate(user=self.user)
        updated_payload = {
            'title': 'Updated iPhone 12',
            'price': '749.99'
        }
        response = self.client.patch(
            reverse('listing-detail', kwargs={'pk': self.listing.pk}),
            data=updated_payload
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.listing.refresh_from_db()
        self.assertEqual(self.listing.title, 'Updated iPhone 12')
        self.assertEqual(float(self.listing.price), 749.99)

    def test_delete_listing(self):
        """
        Test deleting an existing listing.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(
            reverse('listing-detail', kwargs={'pk': self.listing.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Listing.objects.filter(pk=self.listing.pk).exists())


class CategoryListTest(TestCase):
    """
    Test case for the CategoryList view.
    """

    def setUp(self):
        self.client = APIClient()
        self.category1 = Category.objects.create(name="Electronics")
        self.category2 = Category.objects.create(name="Clothing")

    def test_get_all_categories(self):
        """
        Test retrieving all categories.
        """
        response = self.client.get(reverse('category-list'))
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SubcategoryListTest(TestCase):
    """
    Test case for the SubcategoryList view.
    """

    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(name="Electronics")
        self.subcategory1 = Subcategory.objects.create(
            name="Smartphones", category=self.category)
        self.subcategory2 = Subcategory.objects.create(
            name="Laptops", category=self.category)

    def test_get_all_subcategories(self):
        """
        Test retrieving all subcategories.
        """
        response = self.client.get(reverse('subcategory-list'))
        subcategories = Subcategory.objects.all()
        serializer = SubcategorySerializer(subcategories, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_subcategories_by_category(self):
        """
        Test retrieving subcategories for a specific category.
        """
        response = self.client.get(
            reverse('subcategory-by-category',
                    kwargs={'category_id': self.category.id}))
        subcategories = Subcategory.objects.filter(category=self.category)
        serializer = SubcategorySerializer(subcategories, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class MyListingsViewTest(TestCase):
    """
    Test case for the MyListingsView.
    """

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com",
            password="testpass123")
        self.category = Category.objects.create(name="Electronics")
        self.subcategory = Subcategory.objects.create(
            name="Smartphones", category=self.category)
        self.listing1 = Listing.objects.create(
            title="iPhone 12",
            description="Brand new iPhone 12",
            user=self.user,
            category=self.category,
            subcategory=self.subcategory,
            price=799.99,
            condition="new"
        )
        self.listing2 = Listing.objects.create(
            title="Samsung Galaxy S21",
            description="Brand new Samsung Galaxy S21",
            user=self.user,
            category=self.category,
            subcategory=self.subcategory,
            price=899.99,
            condition="new"
        )

    def test_get_my_listings(self):
        """
        Test retrieving listings for the authenticated user.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('my-listings'))
        listings = Listing.objects.filter(user=self.user)
        serializer = ListingSerializer(listings, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class FavoriteListViewTest(TestCase):
    """
    Test case for the FavoriteListView.
    """

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com",
            password="testpass123")
        self.category = Category.objects.create(name="Electronics")
        self.subcategory = Subcategory.objects.create(
            name="Smartphones", category=self.category)
        self.listing1 = Listing.objects.create(
            title="iPhone 12",
            description="Brand new iPhone 12",
            user=self.user,
            category=self.category,
            subcategory=self.subcategory,
            price=799.99,
            condition="new"
        )
        self.listing2 = Listing.objects.create(
            title="Samsung Galaxy S21",
            description="Brand new Samsung Galaxy S21",
            user=self.user,
            category=self.category,
            subcategory=self.subcategory,
            price=899.99,
            condition="new"
        )
        self.listing1.favorited_by.add(self.user)

    def test_get_favorite_listings(self):
        """
        Test retrieving favorite listings for the authenticated user.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('favorite-list'))
        favorite_listings = self.user.favorite_listings.all()
        serializer = ListingSerializer(
            favorite_listings, many=True,
            context={'request': response.wsgi_request}
        )
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class FavoriteToggleViewTest(TestCase):
    """
    Test case for the FavoriteToggleView.
    """

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com",
            password="testpass123")
        self.category = Category.objects.create(name="Electronics")
        self.subcategory = Subcategory.objects.create(
            name="Smartphones", category=self.category)
        self.listing = Listing.objects.create(
            title="iPhone 12",
            description="Brand new iPhone 12",
            user=self.user,
            category=self.category,
            subcategory=self.subcategory,
            price=799.99,
            condition="new"
        )

    def test_toggle_favorite(self):
        """
        Test toggling the favorite status of a listing.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            reverse('favorite-toggle', kwargs={'pk': self.listing.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['action'], 'favorited')
        self.assertTrue(self.listing.favorited_by.filter(
            id=self.user.id).exists())

        response = self.client.post(
            reverse('favorite-toggle', kwargs={'pk': self.listing.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['action'], 'unfavorited')
        self.assertFalse(self.listing.favorited_by.filter(
            id=self.user.id).exists())

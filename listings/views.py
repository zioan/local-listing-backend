from django.db.models import Q
from rest_framework import (
    generics, permissions, status,
    viewsets, filters as drf_filters
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Subcategory, Listing, ListingImage
from .serializers import (
    CategorySerializer,
    SubcategorySerializer,
    ListingSerializer
)
from cloudinary import uploader
from .filters import ListingFilter


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners to edit their listings.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class ListingPagination(PageNumberPagination):
    """
    Pagination settings for listing views.

    Sets default page size and allows clients to specify their own.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class ListingViewSet(viewsets.ModelViewSet):
    """
    Viewset for managing listings.

    Provides actions for listing, creating, retrieving, updating,
    and deleting listings with pagination and filtering.
    """
    queryset = Listing.objects.all().order_by('-created_at')
    serializer_class = ListingSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly
    ]
    pagination_class = ListingPagination
    filter_backends = (
        DjangoFilterBackend,
        drf_filters.SearchFilter,
        drf_filters.OrderingFilter
    )
    filterset_class = ListingFilter
    search_fields = ['title', 'description',
                     'category__name', 'subcategory__name']
    ordering_fields = ['price', 'created_at', 'view_count', 'favorite_count']

    def perform_create(self, serializer):
        """
        Save the listing with the authenticated user
        and set status to 'active'.
        """
        serializer.save(user=self.request.user, status='active')
        self.request.user.profile.update_listing_counts()

    def get_queryset(self):
        """
        Filter queryset based on search term from request parameters.
        """
        queryset = super().get_queryset()
        search_term = self.request.query_params.get('search', None)
        if search_term:
            queryset = queryset.filter(
                Q(title__icontains=search_term) |
                Q(description__icontains=search_term) |
                Q(category__name__icontains=search_term) |
                Q(subcategory__name__icontains=search_term)
            )
        if self.action == 'list':
            queryset = queryset.select_related(
                'user', 'category', 'subcategory')
            queryset = queryset.prefetch_related('images')
        return queryset

    def update(self, request, *args, **kwargs):
        """
        Update an existing listing and handle image updates.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Handle image updates
        self._handle_image_updates(instance, request.data)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        instance.user.profile.update_listing_counts()
        return Response(serializer.data)

    def _handle_image_updates(self, instance, data):
        """
        Update images associated with the listing.

        Deletes images not in the existing list and adds new ones.
        """
        existing_image_ids = data.getlist('existing_images')
        new_images = data.getlist('new_images')

        # Remove images not in existing_image_ids
        images_to_delete = instance.images.exclude(id__in=existing_image_ids)
        for image in images_to_delete:
            self._delete_image(image)

        # Add new images
        for image in new_images:
            ListingImage.objects.create(listing=instance, image=image)

    def _delete_image(self, image):
        """
        Delete an image from Cloudinary and from the database.
        """
        try:
            uploader.destroy(image.image.public_id)
        except Exception as e:
            print(f"Error deleting image from Cloudinary: {e}")
        image.delete()

    def perform_destroy(self, instance):
        """
        Delete a listing and all associated images.
        """
        for image in instance.images.all():
            self._delete_image(image)
        instance.delete()
        instance.user.profile.update_listing_counts()

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a listing and increment its view count.
        """
        instance = self.get_object()
        instance.view_count += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class ListingStatusUpdateView(APIView):
    """
    View for updating the status of a listing.
    """
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        """
        Update the status of a listing.
        """
        try:
            listing = Listing.objects.get(pk=pk)
        except Listing.DoesNotExist:
            return Response({"error": "Listing not found"},
                            status=status.HTTP_404_NOT_FOUND)

        if listing.user != request.user:
            return Response({"error": "You don't have permissions"},
                            status=status.HTTP_403_FORBIDDEN)

        new_status = request.data.get('status')
        if not new_status:
            return Response({"error": "Status is required"},
                            status=status.HTTP_400_BAD_REQUEST)

        listing.status = new_status
        listing.save()

        serializer = ListingSerializer(listing)
        return Response(serializer.data)


class CategoryList(generics.ListAPIView):
    """
    List all categories.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CategoryDetail(generics.RetrieveAPIView):
    """
    Retrieve details of a specific category.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class SubcategoryList(generics.ListAPIView):
    """
    List all subcategories.
    """
    queryset = Subcategory.objects.all()
    serializer_class = SubcategorySerializer


class SubcategoryDetail(generics.RetrieveAPIView):
    """
    Retrieve details of a specific subcategory.
    """
    queryset = Subcategory.objects.all()
    serializer_class = SubcategorySerializer


class SubcategoryByCategory(generics.ListAPIView):
    """
    List subcategories for a specific category.
    """
    serializer_class = SubcategorySerializer

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return Subcategory.objects.filter(category_id=category_id)


class ListingList(generics.ListCreateAPIView):
    """
    List all listings or create a new listing.
    """
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_context(self):
        """
        Include request context in serializer.
        """
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def perform_create(self, serializer):
        """
        Save the listing with the authenticated user.
        """
        serializer.save(user=self.request.user)


class MyListingsView(generics.ListAPIView):
    """
    List all listings created by the authenticated user.
    """
    serializer_class = ListingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Listing.objects.filter(user=self.request.user)


class FavoriteListView(generics.ListAPIView):
    """
    List all listings favorited by the authenticated user.
    """
    serializer_class = ListingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.favorite_listings.all()


class FavoriteToggleView(APIView):
    """
    View for toggling the favorite status of a listing.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        """
        Add or remove a listing from the user's favorites.
        """
        try:
            listing = Listing.objects.get(pk=pk)
        except Listing.DoesNotExist:
            return Response({"detail": "Listing not found."},
                            status=status.HTTP_404_NOT_FOUND)

        user = request.user
        if user in listing.favorited_by.all():
            listing.favorited_by.remove(user)
            action = 'unfavorited'
        else:
            listing.favorited_by.add(user)
            action = 'favorited'

        listing.update_favorite_count()

        serializer = ListingSerializer(listing, context={'request': request})
        return Response({
            "action": action,
            "listing": serializer.data
        }, status=status.HTTP_200_OK)

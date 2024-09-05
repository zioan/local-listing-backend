from rest_framework import generics, permissions, status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters import rest_framework as filters
from .models import Category, Subcategory, Listing, ListingImage
from .serializers import (
    CategorySerializer,
    SubcategorySerializer,
    ListingSerializer
)
from cloudinary import uploader


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class ListingPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class ListingFilter(filters.FilterSet):
    min_price = filters.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = filters.NumberFilter(field_name="price", lookup_expr='lte')
    category = filters.NumberFilter(field_name="category__id")

    class Meta:
        model = Listing
        fields = ['min_price', 'max_price', 'category', 'condition']


class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all().order_by('-created_at')
    serializer_class = ListingSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    pagination_class = ListingPagination
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ListingFilter

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == 'list':
            queryset = queryset.select_related(
                'user', 'category', 'subcategory')
            queryset = queryset.prefetch_related('images')
        return queryset


class CategoryList(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CategoryDetail(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class SubcategoryList(generics.ListAPIView):
    queryset = Subcategory.objects.all()
    serializer_class = SubcategorySerializer


class SubcategoryDetail(generics.RetrieveAPIView):
    queryset = Subcategory.objects.all()
    serializer_class = SubcategorySerializer


class SubcategoryByCategory(generics.ListAPIView):
    serializer_class = SubcategorySerializer

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return Subcategory.objects.filter(category_id=category_id)


class ListingList(generics.ListCreateAPIView):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ListingDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.view_count += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
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

        return Response(serializer.data)

    def _handle_image_updates(self, instance, data):
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
        try:
            uploader.destroy(image.image.public_id)
        except Exception as e:
            print(f"Error deleting image from Cloudinary: {e}")
        image.delete()

    def perform_destroy(self, instance):
        # Delete all associated images
        for image in instance.images.all():
            self._delete_image(image)
        # Delete the listing
        instance.delete()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"detail": "Listing successfully deleted."},
                        status=status.HTTP_204_NO_CONTENT)


class MyListingsView(generics.ListAPIView):
    serializer_class = ListingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Listing.objects.filter(user=self.request.user)


class FavoriteListView(generics.ListAPIView):
    serializer_class = ListingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.favorite_listings.all()


class FavoriteToggleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
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

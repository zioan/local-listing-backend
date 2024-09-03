from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
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


class ListingFavorite(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        listing = generics.get_object_or_404(Listing, pk=pk)
        listing.favorite_count += 1
        listing.save()
        return Response({'status': 'listing favorited'},
                        status=status.HTTP_200_OK)


class ListingUnfavorite(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        listing = generics.get_object_or_404(Listing, pk=pk)
        if listing.favorite_count > 0:
            listing.favorite_count -= 1
            listing.save()
        return Response({'status': 'listing unfavorited'},
                        status=status.HTTP_200_OK)

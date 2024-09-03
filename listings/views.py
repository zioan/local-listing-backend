from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Category, Subcategory, Listing, ListingImage
from .serializers import (
    CategorySerializer,
    SubcategorySerializer,
    ListingSerializer
)


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

        if 'images' in request.FILES:
            for image in request.FILES.getlist('images'):
                ListingImage.objects.create(listing=instance, image=image)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()


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

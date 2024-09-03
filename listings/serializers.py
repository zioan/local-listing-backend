from rest_framework import serializers
from .models import Category, Subcategory, Listing, ListingImage


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class SubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = ['id', 'name', 'category']


class ListingImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingImage
        fields = ['id', 'image', 'created_at']


class ListingSerializer(serializers.ModelSerializer):
    images = ListingImageSerializer(many=True, read_only=True)
    category_name = serializers.ReadOnlyField(source='category.name')
    subcategory_name = serializers.ReadOnlyField(source='subcategory.name')
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Listing
        fields = ['id', 'title', 'description', 'price', 'price_type',
                  'condition', 'category', 'category_name', 'subcategory',
                  'subcategory_name', 'delivery_option', 'user', 'created_at',
                  'updated_at', 'is_active', 'view_count', 'favorite_count',
                  'images']
        read_only_fields = ['user', 'view_count', 'favorite_count']

    def create(self, validated_data):
        images_data = self.context.get('view').request.FILES
        listing = Listing.objects.create(**validated_data)

        for image_data in images_data.values():
            ListingImage.objects.create(listing=listing, image=image_data)

        return listing

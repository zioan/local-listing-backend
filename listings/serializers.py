from rest_framework import serializers
from .models import Category, Subcategory, Listing, ListingImage
from messaging.models import Conversation


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
    is_favorited = serializers.SerializerMethodField()
    has_conversation = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = ['id', 'title', 'description', 'user', 'listing_type',
                  'category', 'category_name', 'subcategory',
                  'subcategory_name', 'price', 'price_type', 'condition',
                  'delivery_option', 'location', 'event_date', 'created_at',
                  'updated_at', 'is_active', 'status', 'view_count',
                  'favorite_count', 'images', 'is_favorited',
                  'has_conversation']
        read_only_fields = ['user', 'view_count',
                            'favorite_count', 'is_favorited']

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorited_by.filter(id=request.user.id).exists()
        return False

    def get_has_conversation(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Conversation.objects.filter(
                listing=obj,
                participants=request.user
            ).exists()
        return False

    def validate(self, data):
        listing_type = data.get('listing_type')
        price = data.get('price')
        price_type = data.get('price_type')
        condition = data.get('condition')
        event_date = data.get('event_date')

        if listing_type in ['item_sale', 'service', 'job', 'housing']:
            if not price and price_type not in ['contact', 'na']:
                raise serializers.ValidationError({
                    'price': (
                        "Price is required for this listing type unless "
                        "'Contact for Price'or 'Not Applicable' is selected."
                    )
                })

        if listing_type == 'item_free':
            data['price'] = 0
            data['price_type'] = 'free'

        if listing_type in ['item_sale', 'item_free', 'item_wanted']:
            if not condition:
                raise serializers.ValidationError({
                    'condition': "Condition is required for item listings."
                })

        if listing_type == 'event':
            if not event_date:
                raise serializers.ValidationError({
                    'event_date': "Event date is required for event listings."
                })

        return data

    def create(self, validated_data):
        images_data = self.context.get('view').request.FILES
        listing = Listing.objects.create(**validated_data)

        for image_data in images_data.values():
            try:
                ListingImage.objects.create(listing=listing, image=image_data)
            except Exception as e:
                print(f"Error uploading image: {str(e)}")

        return listing

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)

        images_data = self.context.get('view').request.FILES
        for image_data in images_data.values():
            ListingImage.objects.create(listing=instance, image=image_data)

        return instance

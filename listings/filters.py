from django_filters import rest_framework as filters
from .models import Listing


class ListingFilter(filters.FilterSet):
    min_price = filters.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = filters.NumberFilter(field_name="price", lookup_expr='lte')
    category = filters.NumberFilter(field_name="category__id")
    subcategory = filters.NumberFilter(field_name="subcategory__id")
    condition = filters.CharFilter(field_name="condition")
    delivery_option = filters.CharFilter(field_name="delivery_option")
    listing_type = filters.CharFilter(field_name="listing_type")
    location = filters.CharFilter(
        field_name="location", lookup_expr='icontains')

    start_date = filters.DateTimeFilter(
        field_name="event_date", lookup_expr='gte')
    end_date = filters.DateTimeFilter(
        field_name="event_date", lookup_expr='lte')

    class Meta:
        model = Listing
        fields = ['min_price', 'max_price', 'category', 'subcategory',
                  'condition', 'delivery_option', 'listing_type', 'location']

from django.contrib import admin
from .models import Category, Subcategory, Listing, ListingImage


class SubcategoryInline(admin.TabularInline):
    """
    Inline admin for Subcategory model in CategoryAdmin.
    """
    model = Subcategory
    extra = 1  # Number of empty forms to display


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin interface for the Category model.
    """
    list_display = ('name', 'subcategory_count')
    search_fields = ('name',)
    inlines = [SubcategoryInline]

    def subcategory_count(self, obj):
        """
        Count the number of subcategories associated with the category.

        Args:
            obj: The Category instance being displayed.

        Returns:
            int: The number of related Subcategory instances.
        """
        return obj.subcategories.count()
    subcategory_count.short_description = 'Number of Subcategories'


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    """
    Admin interface for the Subcategory model.
    """
    list_display = ('name', 'category', 'listing_count')
    list_filter = ('category',)
    search_fields = ('name', 'category__name')

    def listing_count(self, obj):
        """
        Count the number of listings associated with the subcategory.

        Args:
            obj: The Subcategory instance being displayed.

        Returns:
            int: The number of related Listing instances.
        """
        return obj.listings.count()
    listing_count.short_description = 'Number of Listings'


class ListingImageInline(admin.TabularInline):
    """
    Inline admin for ListingImage model in ListingAdmin.
    """
    model = ListingImage
    extra = 1
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        """
        Provide a URL for the image to display a preview.

        Args:
            obj: The ListingImage instance being displayed.

        Returns:
            str: The URL of the image for preview.
        """
        return obj.image.url
    image_preview.short_description = 'Image Preview'


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    """
    Admin interface for the Listing model.
    """
    list_display = ('title', 'user', 'category', 'subcategory',
                    'price', 'condition', 'is_active', 'created_at')
    list_filter = ('category', 'subcategory', 'condition',
                   'is_active', 'created_at')
    search_fields = ('title', 'description', 'user__username')
    readonly_fields = ('view_count', 'favorite_count',
                       'created_at', 'updated_at')
    inlines = [ListingImageInline]

    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'user', 'status')
        }),
        ('Category Information', {
            'fields': ('category', 'subcategory')
        }),
        ('Pricing and Condition', {
            'fields': ('price', 'price_type', 'condition')
        }),
        ('Delivery Information', {
            'fields': ('delivery_option',),
            'classes': ('collapse',)  # Collapsible section
        }),
        ('Listing Status', {
            'fields': ('is_active',)
        }),
        ('Statistics', {
            'fields': ('view_count', 'favorite_count'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # Collapsible section
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        """
        Determine which fields should be readonly based on the object state.

        Args:
            request: The current request object.
            obj: The Listing instance being edited, if applicable.

        Returns:
            tuple: A tuple of field names that should be readonly.
        """
        if obj:  # editing an existing object
            return self.readonly_fields + ('user',)
        return self.readonly_fields


# Register ListingImage model with the admin site
admin.site.register(ListingImage)

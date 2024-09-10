from django.contrib import admin
from .models import Category, Subcategory, Listing, ListingImage


class SubcategoryInline(admin.TabularInline):
    model = Subcategory
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'subcategory_count')
    search_fields = ('name',)
    inlines = [SubcategoryInline]

    def subcategory_count(self, obj):
        return obj.subcategories.count()
    subcategory_count.short_description = 'Number of Subcategories'


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'listing_count')
    list_filter = ('category',)
    search_fields = ('name', 'category__name')

    def listing_count(self, obj):
        return obj.listings.count()
    listing_count.short_description = 'Number of Listings'


class ListingImageInline(admin.TabularInline):
    model = ListingImage
    extra = 1
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        return obj.image.url
    image_preview.short_description = 'Image Preview'


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'subcategory',
                    'price', 'condition', 'is_active', 'created_at')
    list_filter = ('category', 'subcategory',
                   'condition', 'is_active', 'created_at')
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
            'classes': ('collapse',)
        }),
        ('Listing Status', {
            'fields': ('is_active',)
        }),
        ('Statistics', {
            'fields': ('view_count', 'favorite_count'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('user',)
        return self.readonly_fields


admin.site.register(ListingImage)

from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin interface for managing reviews."""

    list_display = ('reviewer', 'reviewed_user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('reviewer__username',
                     'reviewed_user__username', 'content')
    readonly_fields = ('created_at',)

    fieldsets = (
        (None, {
            'fields': ('reviewer', 'reviewed_user', 'rating', 'content')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        """Return the queryset of reviews with related
        reviewers and reviewed users."""
        return super().get_queryset(request).select_related(
            'reviewer', 'reviewed_user'
        )

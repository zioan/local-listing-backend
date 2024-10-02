from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    Admin interface for managing user profiles.

    Provides display options and search functionality.
    """
    list_display = (
        'username', 'location', 'total_listings',
        'active_listings', 'rating'
    )
    search_fields = ('user__username', 'location')

    def username(self, obj):
        """Return the username of the associated user."""
        return obj.user.username

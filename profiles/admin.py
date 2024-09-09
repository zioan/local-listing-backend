from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('username', 'location', 'total_listings',
                    'active_listings', 'rating')
    search_fields = ('user__username', 'location')

    def username(self, obj):
        return obj.user.username

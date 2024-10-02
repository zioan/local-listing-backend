from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    """
    Custom admin interface for the CustomUser model, inheriting from UserAdmin.

    This admin provides the ability to view, filter, and modify CustomUser
    instances with additional fields such as email, username,
    and permission-related fields.
    """

    model = CustomUser
    list_display = ('email', 'username', 'is_active',
                    'is_staff', 'is_superuser')
    list_filter = ('is_active', 'is_staff', 'is_superuser')

    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal info', {'fields': ('street', 'zip', 'city')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups',
                       'user_permissions')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'username', 'password1', 'password2',
                'is_active', 'is_staff', 'is_superuser'
            )
        }),
    )

    search_fields = ('email', 'username')
    ordering = ('email',)


admin.site.register(CustomUser, CustomUserAdmin)

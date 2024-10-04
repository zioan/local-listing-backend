

from django.contrib.sitemaps import Sitemap
from listings.models import Listing
from users.models import CustomUser


class StaticViewSitemap(Sitemap):
    """
    Sitemap for static views in the application.

    This sitemap includes URLs for static public pages
    """
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        """
        Returns a list of static view names to be included in the sitemap.

        Returns:
            list: A list of string identifiers for static views.
        """
        return ['home', 'login', 'register', 'forgot-password',
                'cookies', 'terms', 'privacy']

    def location(self, item):
        """
        Returns the URL for a given static view.

        Args:
            item (str): The identifier of the static view.

        Returns:
            str: The URL path for the given static view.
        """
        return f'/{item}' if item != 'home' else '/'


class ListingSitemap(Sitemap):
    """
    Sitemap for active listings in the application.
    """
    changefreq = "daily"
    priority = 0.7

    def items(self):
        """
        Returns all active listings to be included in the sitemap.

        Returns:
            QuerySet: A queryset of active Listing objects.
        """
        return Listing.objects.filter(status='active')

    def location(self, obj):
        """
        Returns the URL for a given listing.

        Args:
            obj (Listing): The Listing object.

        Returns:
            str: The URL path for the given listing.
        """
        return f'/listings/{obj.id}'


class UserProfileSitemap(Sitemap):
    """
    Sitemap for user profiles in the application.
    """
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        """
        Returns all user profiles to be included in the sitemap.

        Returns:
            QuerySet: A queryset of all CustomUser objects.
        """
        return CustomUser.objects.all()

    def location(self, obj):
        """
        Returns the URL for a given user profile.

        Args:
            obj (CustomUser): The CustomUser object.

        Returns:
            str: The URL path for the given user profile.
        """
        return f'/profiles/{obj.username}'



from django.contrib.sitemaps import Sitemap
from .sitemap import StaticViewSitemap, ListingSitemap, UserProfileSitemap


class CustomSitemap(Sitemap):
    """
    A custom sitemap class that combines static views, listings,
    and user profiles.

    This sitemap aggregates items from StaticViewSitemap, ListingSitemap,
    and UserProfileSitemap to create a comprehensive sitemap
    for the entire application.
    """

    def items(self):
        """
        Aggregates items from all sitemaps.

        Returns:
            list: A combined list of all items from static views, listings,
            and user profiles.
        """
        static_items = StaticViewSitemap().items()
        listing_items = ListingSitemap().items()
        profile_items = UserProfileSitemap().items()
        return static_items + list(listing_items) + list(profile_items)

    def location(self, obj):
        """
        Determines the correct location for each type of item.

        Args:
            obj: The item for which to determine the location.

        Returns:
            str: The URL path for the given item.
        """
        if isinstance(obj, str):
            return StaticViewSitemap().location(obj)
        elif hasattr(obj, 'id'):
            return ListingSitemap().location(obj)
        else:
            return UserProfileSitemap().location(obj)

    def changefreq(self, obj):
        """
        Determines the change frequency for each type of item.

        Args:
            obj: The item for which to determine the change frequency.

        Returns:
            str: The change frequency for the given item.
        """
        if isinstance(obj, str):
            return 'daily'
        elif hasattr(obj, 'id'):
            return 'daily'
        else:
            return 'weekly'

    def priority(self, obj):
        """
        Determines the priority for each type of item.

        Args:
            obj: The item for which to determine the priority.

        Returns:
            float: The priority for the given item.
        """
        if isinstance(obj, str):
            return 0.5
        elif hasattr(obj, 'id'):
            return 0.7
        else:
            return 0.6

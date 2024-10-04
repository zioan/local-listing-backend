from django.contrib.sitemaps import Sitemap
from listings.models import Listing


class ListingSitemap(Sitemap):
    """
    Sitemap for dynamically generating URLs for listings.
    """
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        # Return all listings that are available
        return Listing.objects.filter(is_active=True)

    def location(self, obj):
        # Construct the URL dynamically for each listing using its ID
        return f'/listings/{obj.id}/'

    def lastmod(self, obj):
        # Use the last modified date of the listing
        return obj.updated_at

from django.db import models
from django.conf import settings
from django.db.models import Avg


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    total_listings = models.PositiveIntegerField(default=0)
    active_listings = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    num_ratings = models.PositiveIntegerField(default=0)

    def update_listing_counts(self):
        """Update the total and active listings for the user profile."""
        self.total_listings = self.user.listings.count()
        self.active_listings = self.user.listings.filter(
            is_active=True).count()
        self.save()

    @property
    def average_rating(self):
        """Calculate the average rating from reviews received by the user."""
        average_rating = (
            self.user.reviews_received
            .aggregate(Avg('rating'))['rating__avg'] or 0
        )
        return average_rating

    def __str__(self):
        """Return a string representation of the profile."""
        return f"{self.user.username}'s profile"

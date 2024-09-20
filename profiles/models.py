from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Avg


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    total_listings = models.PositiveIntegerField(default=0)
    active_listings = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    num_ratings = models.PositiveIntegerField(default=0)

    def update_listing_counts(self):
        self.total_listings = self.user.listings.count()
        self.active_listings = self.user.listings.filter(
            is_active=True).count()
        self.save()

    @property
    def average_rating(self):
        return self.user.reviews_received.aggregate(Avg('rating'))['rating__avg'] or 0

    def __str__(self):
        return f"{self.user.username}'s profile"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

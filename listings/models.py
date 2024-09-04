from django.db import models
from django.conf import settings
from cloudinary.models import CloudinaryField


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Subcategory(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(
        Category, related_name='subcategories', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('name', 'category')

    def __str__(self):
        return f"{self.category.name} - {self.name}"


class Listing(models.Model):
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('like_new', 'Like New'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    ]

    PRICE_TYPE_CHOICES = [
        ('fixed', 'Fixed Price'),
        ('negotiable', 'Negotiable'),
        ('free', 'Free'),
    ]

    DELIVERY_CHOICES = [
        ('pickup', 'Pickup Only'),
        ('delivery', 'Delivery Available'),
        ('both', 'Pickup or Delivery'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    price_type = models.CharField(
        max_length=20, choices=PRICE_TYPE_CHOICES, default='fixed')
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    category = models.ForeignKey(
        Category,
        related_name='listings',
        on_delete=models.SET_NULL,
        null=True
    )
    subcategory = models.ForeignKey(
        Subcategory,
        related_name='listings',
        on_delete=models.SET_NULL,
        null=True
    )
    delivery_option = models.CharField(
        max_length=20, choices=DELIVERY_CHOICES, blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='listings', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    view_count = models.PositiveIntegerField(default=0)
    favorite_count = models.PositiveIntegerField(default=0)

    favorited_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='favorite_listings',
        blank=True
    )

    def update_favorite_count(self):
        self.favorite_count = self.favorited_by.count()
        self.save()

    def __str__(self):
        return self.title


class ListingImage(models.Model):
    listing = models.ForeignKey(
        Listing, related_name='images', on_delete=models.CASCADE)
    image = CloudinaryField('image')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.listing.title}"

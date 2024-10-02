from django.db import models
from django.conf import settings
from cloudinary.models import CloudinaryField


class Category(models.Model):
    """
    Model representing a category of listings.

    Attributes:
        name (str): The name of the category, unique for each category.
    """
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Subcategory(models.Model):
    """
    Model representing a subcategory under a specific category.

    Attributes:
        name (str): The name of the subcategory.
        category (Category): The category to which this subcategory belongs.
    """
    name = models.CharField(max_length=100)
    category = models.ForeignKey(
        Category, related_name='subcategories', on_delete=models.CASCADE)

    class Meta:
        # Ensure unique name per category
        unique_together = ('name', 'category')

    def __str__(self):
        return f"{self.category.name} - {self.name}"


class Listing(models.Model):
    """
    Model representing a listing for sale, wanted, or other types.

    Attributes:
        title (str): The title of the listing.
        description (str): The description of the listing.
        user (User): The user who created the listing.
        listing_type (str): The type of listing.
        category (Category): The category of the listing.
        subcategory (Subcategory): The subcategory of the listing.
        price (Decimal): The price of the listing.
        price_type (str): The pricing type (fixed, negotiable, etc.).
        condition (str): The condition of the item.
        delivery_option (str): The delivery option available.
        location (str): The location of the listing.
        event_date (datetime): The date for events, if applicable.
        created_at (datetime): Timestamp when the listing was created.
        updated_at (datetime): Timestamp when the listing was last updated.
        is_active (bool): Indicates if the listing is active.
        status (str): The current status of the listing.
        view_count (int): Number of times the listing has been viewed.
        favorite_count (int): Number of times the listing has been favorited.
        favorited_by (ManyToManyField): Users who have favorited the listing.
    """
    LISTING_TYPE_CHOICES = [
        ('item_sale', 'Item for Sale'),
        ('item_free', 'Free Item'),
        ('item_wanted', 'Item Wanted'),
        ('service', 'Service'),
        ('job', 'Job'),
        ('housing', 'Housing'),
        ('event', 'Event'),
        ('other', 'Other'),
    ]

    CONDITION_CHOICES = [
        ('new', 'New'),
        ('like_new', 'Like New'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
        ('na', 'Not Applicable'),
    ]

    PRICE_TYPE_CHOICES = [
        ('fixed', 'Fixed Price'),
        ('negotiable', 'Negotiable'),
        ('free', 'Free'),
        ('contact', 'Contact for Price'),
        ('na', 'Not Applicable'),
    ]

    DELIVERY_CHOICES = [
        ('pickup', 'Pickup Only'),
        ('delivery', 'Delivery Available'),
        ('both', 'Pickup or Delivery'),
        ('na', 'Not Applicable'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('pending', 'Pending'),
        ('sold', 'Sold'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='listings', on_delete=models.CASCADE)
    listing_type = models.CharField(
        max_length=30,
        choices=LISTING_TYPE_CHOICES,
        default='other'
    )
    category = models.ForeignKey(
        Category,
        related_name='listings',
        on_delete=models.SET_NULL,
        null=True)
    subcategory = models.ForeignKey(
        Subcategory,
        related_name='listings',
        on_delete=models.SET_NULL,
        null=True,
        blank=True)

    price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    price_type = models.CharField(
        max_length=20, choices=PRICE_TYPE_CHOICES, default='fixed')
    condition = models.CharField(
        max_length=20, choices=CONDITION_CHOICES, blank=True, null=True)
    delivery_option = models.CharField(
        max_length=20, choices=DELIVERY_CHOICES, default='na')

    location = models.CharField(max_length=255, blank=True)
    event_date = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='active')
    view_count = models.PositiveIntegerField(default=0)
    favorite_count = models.PositiveIntegerField(default=0)
    favorited_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='favorite_listings',
        blank=True)

    def save(self, *args, **kwargs):
        """
        Override save method to set is_active based on status.
        """
        self.is_active = self.status == 'active'
        super().save(*args, **kwargs)

    def update_favorite_count(self):
        """
        Update the favorite count based on users who have
        favorited this listing.
        """
        self.favorite_count = self.favorited_by.count()
        self.save()

    def __str__(self):
        return self.title


class ListingImage(models.Model):
    """
    Model representing an image associated with a listing.

    Attributes:
        listing (Listing): The listing to which this image belongs.
        image (CloudinaryField): The image file.
        created_at (datetime): Timestamp when the image was created.
    """
    listing = models.ForeignKey(
        Listing, related_name='images', on_delete=models.CASCADE)
    image = CloudinaryField('image')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.listing.title}"

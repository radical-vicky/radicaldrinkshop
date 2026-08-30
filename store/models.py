from django.conf import settings
from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=110, unique=True)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category, related_name='products', on_delete=models.CASCADE
    )
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=160, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, help_text='Price in KES')
    volume_ml = models.PositiveIntegerField(
        blank=True, null=True, help_text='e.g. 500 for a 500ml bottle'
    )
    stock = models.PositiveIntegerField(default=0)
    is_alcoholic = models.BooleanField(
        default=False,
        help_text='Alcoholic drinks may be restricted from online sale/delivery.',
    )
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(
        default=False,
        help_text='Show this product in the homepage hero slider.',
    )
    hero_tagline = models.CharField(
        max_length=60, blank=True,
        help_text='Short badge text for the hero slide, e.g. "20% off today". Defaults to "Featured".'
    )
    hero_headline = models.CharField(
        max_length=100, blank=True,
        help_text='Big hero headline. Defaults to the product name if left blank.'
    )
    hero_description = models.CharField(
        max_length=200, blank=True,
        help_text='Short hero copy. Defaults to the product description if left blank.'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('store:product_detail', args=[self.slug])

    @property
    def in_stock(self):
        return self.stock > 0

    @property
    def is_deliverable(self):
        """Respects the DISALLOW_ALCOHOL_DELIVERY setting."""
        from django.conf import settings as dj_settings
        if self.is_alcoholic and dj_settings.DISALLOW_ALCOHOL_DELIVERY:
            return False
        return True


class SiteSettings(models.Model):
    """Sitewide look-and-feel controls editable from /admin/ — no code
    changes needed to swap the background image.

    Upload any image you have the rights to use (your own photography, a
    properly licensed stock photo, etc.) — it's stored on Cloudinary like
    product images. Only one row is used at a time: the most recent
    active one.
    """
    name = models.CharField(
        max_length=100, default='Default', help_text='Just a label for you, e.g. "Festive season".'
    )
    background_image = models.ImageField(
        upload_to='site/', blank=True, null=True,
        help_text='Sitewide ambient background, shown dimmed behind the glass UI.'
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'site settings'

    def __str__(self):
        return self.name


class DeliveryZone(models.Model):
    """A neighbourhood/estate with its own delivery fee and ETA.

    Matching is done by case-insensitive substring against
    DeliveryAddress.area — e.g. a zone named "Kilimani" matches an address
    with area "Kilimani" or "Kilimani, near Yaya Centre".
    """

    name = models.CharField(max_length=150, unique=True, help_text='e.g. Kilimani, Westlands')
    delivery_fee = models.DecimalField(max_digits=8, decimal_places=2, help_text='Fee in KES')
    estimated_minutes = models.PositiveIntegerField(
        default=45, help_text='Typical delivery time for this zone, in minutes'
    )
    is_active = models.BooleanField(
        default=True, help_text='Turn off to stop deliveries to this zone.'
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} — KES {self.delivery_fee}'


class DeliveryAddress(models.Model):
    """A saved apartment / doorstep delivery address for a customer."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='addresses', on_delete=models.CASCADE
    )
    label = models.CharField(
        max_length=50, default='Home', help_text='e.g. Home, Office'
    )
    full_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=20, help_text='Used for M-Pesa STK push, e.g. 2547XXXXXXXX')
    building_name = models.CharField(max_length=150)
    apartment_number = models.CharField(max_length=50, blank=True)
    floor = models.CharField(max_length=20, blank=True)
    street = models.CharField(max_length=200)
    area = models.CharField(max_length=150, help_text='Neighbourhood / estate')
    city = models.CharField(max_length=100, default='Nairobi')
    delivery_notes = models.TextField(
        blank=True, help_text='Gate code, landmark, preferred drop-off instructions, etc.'
    )
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True,
        help_text='Captured from the browser/device GPS, if allowed.'
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True,
        help_text='Captured from the browser/device GPS, if allowed.'
    )
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'delivery addresses'

    def __str__(self):
        return f'{self.label} — {self.building_name}, {self.area}'

    @property
    def has_gps(self):
        return self.latitude is not None and self.longitude is not None

    @property
    def maps_url(self):
        if self.has_gps:
            return f'https://www.google.com/maps?q={self.latitude},{self.longitude}'
        return None

    def as_text(self):
        parts = [
            self.building_name,
            f'Apt {self.apartment_number}' if self.apartment_number else '',
            f'Floor {self.floor}' if self.floor else '',
            self.street,
            self.area,
            self.city,
        ]
        return ', '.join(p for p in parts if p)

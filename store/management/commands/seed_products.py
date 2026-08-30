from django.core.management.base import BaseCommand
from django.utils.text import slugify

from store.models import Category, DeliveryZone, Product

SAMPLE_ZONES = [
    ('Kilimani', 100, 30),
    ('Westlands', 120, 35),
    ('Lavington', 120, 35),
    ('Kileleshwa', 100, 30),
    ('South B', 150, 45),
    ('South C', 150, 45),
]

SAMPLE = {
    'Sodas': [
        ('Coca-Cola 500ml', 80, 500),
        ('Fanta Orange 500ml', 80, 500),
        ('Sprite 500ml', 80, 500),
    ],
    'Juices': [
        ('Del Monte Mango 1L', 220, 1000),
        ('Minute Maid Pulpy Orange 1L', 210, 1000),
    ],
    'Water': [
        ('Dasani Water 500ml', 50, 500),
        ('Keringet Water 1L', 90, 1000),
    ],
    'Energy Drinks': [
        ('Red Bull 250ml', 250, 250),
        ('Monster Energy 500ml', 300, 500),
    ],
}


FEATURED = {
    'Coca-Cola 500ml': ('20% off today', 'Chilled sodas, at your door', ''),
    'Del Monte Mango 1L': ('New arrivals', 'Real fruit juices, restocked weekly', ''),
    'Red Bull 250ml': ('Weekend pick', 'Fuel your night out', ''),
}


class Command(BaseCommand):
    help = 'Seed the database with sample non-alcoholic drink categories/products.'

    def handle(self, *args, **options):
        for zone_name, fee, minutes in SAMPLE_ZONES:
            DeliveryZone.objects.get_or_create(
                name=zone_name,
                defaults={'delivery_fee': fee, 'estimated_minutes': minutes},
            )

        for category_name, products in SAMPLE.items():
            category, _ = Category.objects.get_or_create(
                name=category_name, slug=slugify(category_name)
            )
            for name, price, volume_ml in products:
                tagline, headline, description = FEATURED.get(name, ('', '', ''))
                Product.objects.get_or_create(
                    name=name,
                    defaults={
                        'category': category,
                        'slug': slugify(name),
                        'price': price,
                        'volume_ml': volume_ml,
                        'stock': 100,
                        'is_alcoholic': False,
                        'is_active': True,
                        'is_featured': name in FEATURED,
                        'hero_tagline': tagline,
                        'hero_headline': headline,
                        'hero_description': description,
                    },
                )
        self.stdout.write(self.style.SUCCESS('Sample drinks seeded.'))

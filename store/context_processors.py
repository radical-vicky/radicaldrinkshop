from .cart import Cart
from .models import SiteSettings


def cart(request):
    return {'cart': Cart(request)}


def site_settings(request):
    return {'site_settings': SiteSettings.objects.filter(is_active=True).order_by('-id').first()}

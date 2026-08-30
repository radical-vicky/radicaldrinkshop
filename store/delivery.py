from django.conf import settings

from .models import DeliveryZone


def resolve_zone(address):
    """Find the best-matching active DeliveryZone for a DeliveryAddress.

    Matches by case-insensitive substring against the address's `area`
    field. Returns None if no zone matches (caller should fall back to the
    default flat DELIVERY_FEE) or if the matched zone is inactive
    (deliveries currently unavailable there).
    """
    if not address:
        return None
    area = (address.area or '').strip().lower()
    if not area:
        return None
    for zone in DeliveryZone.objects.all():
        if zone.name.strip().lower() in area or area in zone.name.strip().lower():
            return zone
    return None


def get_delivery_fee(address):
    """Return (fee, zone_or_None, is_deliverable)."""
    zone = resolve_zone(address)
    if zone is None:
        return settings.DELIVERY_FEE, None, True
    if not zone.is_active:
        return None, zone, False
    return zone.delivery_fee, zone, True

from django.contrib import admin

from .models import Category, DeliveryAddress, DeliveryZone, Product, SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'background_image')
    list_filter = ('is_active',)


@admin.register(DeliveryZone)
class DeliveryZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'delivery_fee', 'estimated_minutes', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'is_alcoholic', 'is_active', 'is_featured')
    list_filter = ('category', 'is_alcoholic', 'is_active', 'is_featured')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        (None, {'fields': ('category', 'name', 'slug', 'description', 'image')}),
        ('Pricing & stock', {'fields': ('price', 'volume_ml', 'stock', 'is_alcoholic', 'is_active')}),
        ('Homepage hero slider', {
            'fields': ('is_featured', 'hero_tagline', 'hero_headline', 'hero_description'),
            'description': 'Mark up to a few products as featured to show them in the homepage hero slider, with real product photos.',
        }),
    )


@admin.register(DeliveryAddress)
class DeliveryAddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'label', 'building_name', 'area', 'city', 'has_gps', 'is_default')
    list_filter = ('city', 'is_default')
    search_fields = ('user__username', 'building_name', 'area')
    readonly_fields = ('maps_link',)

    def maps_link(self, obj):
        if obj.has_gps:
            from django.utils.html import format_html
            return format_html('<a href="{}" target="_blank">Open in Google Maps</a>', obj.maps_url)
        return 'No GPS captured'
    maps_link.short_description = 'GPS location'

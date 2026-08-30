from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .cart import Cart
from .models import Category, DeliveryAddress, Product


def home(request):
    category_slug = request.GET.get('category')
    categories = Category.objects.all()
    products = Product.objects.filter(is_active=True).select_related('category')

    selected_category = None
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=selected_category)

    hero_products = list(
        Product.objects.filter(is_active=True, is_featured=True)
        .select_related('category')[:5]
    )
    if not hero_products:
        # Nothing marked as featured yet — fall back to a few in-stock
        # products (preferring ones with a real photo) so the hero never
        # renders empty on a fresh install.
        hero_products = list(
            Product.objects.filter(is_active=True, stock__gt=0)
            .exclude(image='').order_by('-created_at')[:3]
        ) or list(Product.objects.filter(is_active=True)[:3])

    themes = ['green', 'orange', 'gold']
    hero_slides = []
    for i, product in enumerate(hero_products):
        hero_slides.append({
            'product': product,
            'theme': themes[i % len(themes)],
            'badge': product.hero_tagline or 'Featured',
            'headline': product.hero_headline or product.name,
            'description': product.hero_description or product.description or f'KES {product.price} — order now for delivery to your door.',
        })

    return render(request, 'store/home.html', {
        'categories': categories,
        'selected_category': selected_category,
        'products': products,
        'hero_slides': hero_slides,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    return render(request, 'store/product_detail.html', {'product': product})


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, is_active=True)

    if not product.is_deliverable:
        messages.error(
            request,
            f'{product.name} cannot be added — online sale/delivery of this '
            'item is currently restricted.'
        )
        return redirect(request.POST.get('next') or 'store:home')

    quantity = int(request.POST.get('quantity', 1))
    cart.add(product=product, quantity=quantity)
    messages.success(request, f'Added {product.name} to your cart.')
    return redirect(request.POST.get('next') or 'store:cart_detail')


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.info(request, f'Removed {product.name} from your cart.')
    return redirect('store:cart_detail')


@require_POST
def cart_update(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = max(1, int(request.POST.get('quantity', 1)))
    cart.add(product=product, quantity=quantity, replace=True)
    return redirect('store:cart_detail')


def cart_detail(request):
    cart = Cart(request)
    return render(request, 'store/cart.html', {'cart': cart})


@login_required
def address_list(request):
    addresses = request.user.addresses.all()
    return render(request, 'store/address_list.html', {'addresses': addresses})


@login_required
def address_add(request):
    if request.method == 'POST':
        latitude = request.POST.get('latitude') or None
        longitude = request.POST.get('longitude') or None
        DeliveryAddress.objects.create(
            user=request.user,
            label=request.POST.get('label') or 'Home',
            full_name=request.POST.get('full_name'),
            phone_number=request.POST.get('phone_number'),
            building_name=request.POST.get('building_name'),
            apartment_number=request.POST.get('apartment_number', ''),
            floor=request.POST.get('floor', ''),
            street=request.POST.get('street'),
            area=request.POST.get('area'),
            city=request.POST.get('city') or 'Nairobi',
            delivery_notes=request.POST.get('delivery_notes', ''),
            latitude=latitude,
            longitude=longitude,
            is_default=bool(request.POST.get('is_default')),
        )
        messages.success(request, 'Delivery address saved.')
        return redirect('store:address_list')
    return render(request, 'store/address_form.html')

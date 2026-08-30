from decimal import Decimal

from .models import Product

CART_SESSION_KEY = 'cart'


class Cart:
    """A simple session-backed shopping cart.

    Stored in the session as: {"<product_id>": {"quantity": int}}
    Keeping only quantity in the session (not price) means price changes
    on the product are always reflected live.
    """

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_KEY)
        if cart is None:
            cart = self.session[CART_SESSION_KEY] = {}
        self.cart = cart

    def add(self, product, quantity=1, replace=False):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0}
        if replace:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def save(self):
        self.session.modified = True

    def clear(self):
        self.session[CART_SESSION_KEY] = {}
        self.save()

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        products_map = {str(p.id): p for p in products}
        for product_id, item in self.cart.items():
            product = products_map.get(product_id)
            if not product:
                continue
            line = {
                'product': product,
                'quantity': item['quantity'],
                'unit_price': product.price,
                'subtotal': product.price * item['quantity'],
            }
            yield line

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    @property
    def subtotal(self):
        return sum((line['subtotal'] for line in self), Decimal('0.00'))

    def has_undeliverable_items(self):
        return any(not line['product'].is_deliverable for line in self)

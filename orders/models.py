from django.conf import settings
from django.db import models

from store.models import DeliveryAddress, Product


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING_PAYMENT = 'pending_payment', 'Pending payment'
        PAID = 'paid', 'Paid'
        PREPARING = 'preparing', 'Preparing'
        OUT_FOR_DELIVERY = 'out_for_delivery', 'Out for delivery'
        DELIVERED = 'delivered', 'Delivered'
        CANCELLED = 'cancelled', 'Cancelled'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='orders', on_delete=models.CASCADE
    )
    delivery_address = models.ForeignKey(
        DeliveryAddress, related_name='orders', on_delete=models.PROTECT
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING_PAYMENT
    )
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=8, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    phone_number = models.CharField(max_length=20, help_text='Phone used for M-Pesa payment')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Order #{self.id} — {self.user}'

    def mark_paid(self):
        self.status = self.Status.PAID
        self.save(update_fields=['status', 'updated_at'])


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.PROTECT)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.quantity} x {self.product.name}'

    @property
    def subtotal(self):
        return self.unit_price * self.quantity

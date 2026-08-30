from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from payments.mpesa import MpesaError, stk_push
from payments.models import MpesaTransaction
from store.cart import Cart
from store.delivery import get_delivery_fee
from store.models import DeliveryAddress

from .models import Order, OrderItem


@login_required
def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.warning(request, 'Your cart is empty.')
        return redirect('store:home')

    if cart.has_undeliverable_items():
        messages.error(
            request,
            'Your cart contains an item that cannot currently be delivered. '
            'Please remove it to continue.'
        )
        return redirect('store:cart_detail')

    addresses = request.user.addresses.all()
    # Precompute each address's delivery fee/zone so the radio list can show it.
    address_options = []
    for addr in addresses:
        fee, zone, deliverable = get_delivery_fee(addr)
        address_options.append({
            'address': addr,
            'fee': fee,
            'zone': zone,
            'deliverable': deliverable,
            'total': (cart.subtotal + fee) if deliverable else None,
        })

    if request.method == 'POST':
        address_id = request.POST.get('address_id')
        phone_number = request.POST.get('phone_number', '').strip()
        address = get_object_or_404(DeliveryAddress, id=address_id, user=request.user)

        fee, zone, deliverable = get_delivery_fee(address)
        if not deliverable:
            messages.error(
                request,
                f'Sorry, we are not currently delivering to {address.area}. '
                'Please choose a different address.'
            )
            return redirect('orders:checkout')

        if not phone_number:
            phone_number = address.phone_number

        order = Order.objects.create(
            user=request.user,
            delivery_address=address,
            subtotal=cart.subtotal,
            delivery_fee=fee,
            total=cart.subtotal + fee,
            phone_number=phone_number,
        )
        for line in cart:
            OrderItem.objects.create(
                order=order,
                product=line['product'],
                unit_price=line['unit_price'],
                quantity=line['quantity'],
            )

        try:
            response = stk_push(
                phone_number=phone_number,
                amount=order.total,
                account_reference=f'Order{order.id}',
                transaction_desc=f'Payment for order #{order.id}',
            )
            MpesaTransaction.objects.create(
                order=order,
                phone_number=phone_number,
                amount=order.total,
                merchant_request_id=response.get('MerchantRequestID', ''),
                checkout_request_id=response.get('CheckoutRequestID', ''),
            )
        except MpesaError as exc:
            messages.error(
                request,
                'We could not reach M-Pesa to request payment. '
                f'Please try again. ({exc})'
            )
            return redirect('orders:checkout')

        cart.clear()
        messages.success(
            request,
            'Check your phone and enter your M-Pesa PIN to complete payment.'
        )
        return redirect('orders:payment_waiting', order_id=order.id)

    return render(request, 'orders/checkout.html', {
        'cart': cart,
        'address_options': address_options,
    })


@login_required
def payment_waiting(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/payment_waiting.html', {'order': order})


@login_required
def order_history(request):
    orders = request.user.orders.all()
    return render(request, 'orders/order_history.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})

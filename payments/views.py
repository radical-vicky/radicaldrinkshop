import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from orders.models import Order

from .models import MpesaTransaction


@csrf_exempt
@require_POST
def mpesa_callback(request):
    """Safaricom posts the result of an STK push here.

    This endpoint must be publicly reachable (set MPESA_CALLBACK_URL to its
    real, HTTPS URL) and is exempt from CSRF since Safaricom, not a browser,
    calls it.
    """
    try:
        data = json.loads(request.body)
    except (ValueError, TypeError):
        return JsonResponse({'ResultCode': 1, 'ResultDesc': 'Invalid payload'})

    stk_callback = data.get('Body', {}).get('stkCallback', {})
    checkout_request_id = stk_callback.get('CheckoutRequestID')
    result_code = stk_callback.get('ResultCode')
    result_desc = stk_callback.get('ResultDesc', '')

    try:
        txn = MpesaTransaction.objects.get(checkout_request_id=checkout_request_id)
    except MpesaTransaction.DoesNotExist:
        return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Accepted (no matching txn)'})

    txn.result_description = result_desc

    if result_code == 0:
        # Successful payment — pull the M-Pesa receipt number out of the
        # CallbackMetadata items array.
        items = stk_callback.get('CallbackMetadata', {}).get('Item', [])
        metadata = {item.get('Name'): item.get('Value') for item in items}
        txn.mpesa_receipt_number = metadata.get('MpesaReceiptNumber', '')
        txn.status = MpesaTransaction.Status.SUCCESS
        txn.save()

        order = txn.order
        order.mark_paid()
    else:
        txn.status = MpesaTransaction.Status.CANCELLED if result_code == 1032 else MpesaTransaction.Status.FAILED
        txn.save()

    return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Accepted'})


@require_GET
def payment_status(request, order_id):
    """Polled by the checkout-waiting page's JS to see if payment landed."""
    order = Order.objects.filter(id=order_id, user=request.user).first()
    if not order:
        return JsonResponse({'status': 'unknown'}, status=404)

    latest_txn = order.mpesa_transactions.order_by('-created_at').first()
    return JsonResponse({
        'order_status': order.status,
        'txn_status': latest_txn.status if latest_txn else None,
        'txn_message': latest_txn.result_description if latest_txn else '',
    })

"""
Thin wrapper around Safaricom's Daraja API for M-Pesa STK Push (Lipa Na
M-Pesa Online). Docs: https://developer.safaricom.co.ke/APIs/MpesaExpressSimulate

Requires these settings (see drinkshop/settings.py):
MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET, MPESA_SHORTCODE, MPESA_PASSKEY,
MPESA_CALLBACK_URL, MPESA_AUTH_URL, MPESA_STK_PUSH_URL, MPESA_STK_QUERY_URL
"""
import base64
from datetime import datetime

import requests
from django.conf import settings


class MpesaError(Exception):
    pass


def get_access_token():
    response = requests.get(
        settings.MPESA_AUTH_URL,
        auth=(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET),
        timeout=15,
    )
    if response.status_code != 200:
        raise MpesaError(f'Failed to get access token: {response.text}')
    return response.json()['access_token']


def _password_and_timestamp():
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    raw = f'{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}'
    password = base64.b64encode(raw.encode()).decode()
    return password, timestamp


def normalize_phone(phone_number):
    """Convert 07XXXXXXXX / +2547XXXXXXXX / 2547XXXXXXXX to 2547XXXXXXXX."""
    phone = phone_number.strip().replace(' ', '').replace('+', '')
    if phone.startswith('0'):
        phone = '254' + phone[1:]
    return phone


def stk_push(*, phone_number, amount, account_reference, transaction_desc):
    """Trigger an STK push (M-Pesa payment prompt) on the customer's phone.

    Returns the parsed JSON response from Safaricom, which includes
    MerchantRequestID and CheckoutRequestID used to reconcile the callback.
    """
    token = get_access_token()
    password, timestamp = _password_and_timestamp()
    phone = normalize_phone(phone_number)

    payload = {
        'BusinessShortCode': settings.MPESA_SHORTCODE,
        'Password': password,
        'Timestamp': timestamp,
        'TransactionType': 'CustomerPayBillOnline',
        'Amount': int(amount),
        'PartyA': phone,
        'PartyB': settings.MPESA_SHORTCODE,
        'PhoneNumber': phone,
        'CallBackURL': settings.MPESA_CALLBACK_URL,
        'AccountReference': account_reference,
        'TransactionDesc': transaction_desc,
    }
    response = requests.post(
        settings.MPESA_STK_PUSH_URL,
        json=payload,
        headers={'Authorization': f'Bearer {token}'},
        timeout=15,
    )
    if response.status_code != 200:
        raise MpesaError(f'STK push failed: {response.text}')
    return response.json()


def stk_query(checkout_request_id):
    """Poll Safaricom for the outcome of a previously initiated STK push."""
    token = get_access_token()
    password, timestamp = _password_and_timestamp()

    payload = {
        'BusinessShortCode': settings.MPESA_SHORTCODE,
        'Password': password,
        'Timestamp': timestamp,
        'CheckoutRequestID': checkout_request_id,
    }
    response = requests.post(
        settings.MPESA_STK_QUERY_URL,
        json=payload,
        headers={'Authorization': f'Bearer {token}'},
        timeout=15,
    )
    if response.status_code != 200:
        raise MpesaError(f'STK query failed: {response.text}')
    return response.json()

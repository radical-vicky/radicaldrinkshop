from django.urls import path

from . import views

app_name = 'payments'

urlpatterns = [
    path('mpesa/callback/', views.mpesa_callback, name='mpesa_callback'),
    path('status/<int:order_id>/', views.payment_status, name='payment_status'),
]

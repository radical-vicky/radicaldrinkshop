from django.urls import path

from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('waiting/<int:order_id>/', views.payment_waiting, name='payment_waiting'),
    path('history/', views.order_history, name='order_history'),
    path('<int:order_id>/', views.order_detail, name='order_detail'),
]

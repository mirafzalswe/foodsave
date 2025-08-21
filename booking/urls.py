from django.urls import path
from . import views

app_name = 'booking'

urlpatterns = [
    path('cart/', views.CartView.as_view(), name='cart'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('order/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('orders/', views.OrderListView.as_view(), name='order_list'),
]

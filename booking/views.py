from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, TemplateView
from django.db import transaction
from django.http import JsonResponse
from django.urls import reverse_lazy
from .models import Order, OrderItem
from .forms import CheckoutForm, OrderSearchForm
from catalog.models import Offer
import uuid


class CartView(TemplateView):
    template_name = 'booking/cart.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Cart will be handled via JavaScript and localStorage for now
        return context


class CheckoutView(LoginRequiredMixin, CreateView):
    model = Order
    form_class = CheckoutForm
    template_name = 'booking/checkout.html'
    success_url = reverse_lazy('booking:order_list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        
        # Calculate total amount (this would normally come from cart)
        form.instance.total_amount = 0
        form.instance.delivery_fee = 5.00  # Fixed delivery fee for now
        
        with transaction.atomic():
            response = super().form_valid(form)
            
            # Here you would create OrderItems from cart data
            # For now, we'll create a placeholder
            
            messages.success(self.request, f'Заказ {self.object.order_number} успешно создан!')
            return response


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'booking/order_detail.html'
    context_object_name = 'order'
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items__offer__item')


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'booking/order_list.html'
    context_object_name = 'orders'
    paginate_by = 10
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

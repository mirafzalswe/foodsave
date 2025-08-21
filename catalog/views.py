from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import Category, Item, Offer


class CatalogView(ListView):
    model = Item
    template_name = 'catalog/catalog.html'
    context_object_name = 'items'
    paginate_by = 12
    
    def get_queryset(self):
        return Item.objects.filter(is_active=True).select_related('vendor', 'category')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True)
        return context


class CategoryView(ListView):
    model = Item
    template_name = 'catalog/category.html'
    context_object_name = 'items'
    paginate_by = 12
    
    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Item.objects.filter(
            category=self.category, 
            is_active=True
        ).select_related('vendor', 'category')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['categories'] = Category.objects.filter(is_active=True)
        return context


class ItemDetailView(DetailView):
    model = Item
    template_name = 'catalog/item_detail.html'
    context_object_name = 'item'
    
    def get_queryset(self):
        return Item.objects.filter(is_active=True).select_related('vendor', 'category')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['offers'] = self.object.offers.filter(status='available')
        context['images'] = self.object.images.all().order_by('order')
        return context


class SearchView(ListView):
    model = Item
    template_name = 'catalog/search.html'
    context_object_name = 'items'
    paginate_by = 12
    
    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Item.objects.filter(
                Q(title__icontains=query) | 
                Q(description__icontains=query) |
                Q(vendor__name__icontains=query),
                is_active=True
            ).select_related('vendor', 'category')
        return Item.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context

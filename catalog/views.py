from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.http import JsonResponse
import math
from .models import Item, Category
from vendors.models import Vendor, Branch


class CatalogView(ListView):
    model = Item
    template_name = 'catalog/catalog.html'
    context_object_name = 'items'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Item.objects.filter(is_active=True).select_related('vendor', 'category')
        
        # Filter by vendor type (products vs dishes)
        vendor_type = self.request.GET.get('type')
        if vendor_type == 'products':
            # Products from stores
            queryset = queryset.filter(vendor__type='store')
        elif vendor_type == 'dishes':
            # Dishes from restaurants and cafes
            queryset = queryset.filter(vendor__type__in=['restaurant', 'cafe'])
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True)
        context['current_type'] = self.request.GET.get('type', '')
        return context


class CategoryView(ListView):
    model = Item
    template_name = 'catalog/category.html'
    context_object_name = 'items'
    paginate_by = 12
    
    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['category_slug'])
        return Item.objects.filter(category=self.category, is_active=True).select_related('vendor')
    
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


def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points using Haversine formula"""
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c


class MapView(ListView):
    model = Item
    template_name = 'catalog/map_simple.html'
    context_object_name = 'nearby_items'
    
    def get_queryset(self):
        user_lat = float(self.request.GET.get('lat', 0))
        user_lng = float(self.request.GET.get('lng', 0))
        
        if not user_lat or not user_lng:
            return Item.objects.none()
        
        # Get all active items with their branches
        items = Item.objects.filter(is_active=True).select_related('vendor', 'branch', 'category')
        
        # Calculate distances and sort by proximity
        items_with_distance = []
        for item in items:
            if item.branch and item.branch.latitude and item.branch.longitude:
                distance = calculate_distance(
                    user_lat, user_lng,
                    float(item.branch.latitude), 
                    float(item.branch.longitude)
                )
                items_with_distance.append((item, distance))
        
        # Sort by distance and return closest 20 items
        items_with_distance.sort(key=lambda x: x[1])
        return [item for item, distance in items_with_distance[:20]]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_lat = self.request.GET.get('lat')
        user_lng = self.request.GET.get('lng')
        
        context['user_lat'] = user_lat
        context['user_lng'] = user_lng
        
        # Prepare items with distances for the map
        items_data = []
        for item in context['nearby_items']:
            if item.branch and item.branch.latitude and item.branch.longitude:
                distance = calculate_distance(
                    float(user_lat), float(user_lng),
                    float(item.branch.latitude), 
                    float(item.branch.longitude)
                )
                items_data.append({
                    'item': item,
                    'distance': round(distance, 2),
                    'lat': float(item.branch.latitude),
                    'lng': float(item.branch.longitude)
                })
        
        context['items_data'] = items_data
        return context

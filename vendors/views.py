from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Vendor, Branch


class VendorListView(ListView):
    model = Vendor
    template_name = 'vendors/vendor_list.html'
    context_object_name = 'vendors'
    paginate_by = 12
    
    def get_queryset(self):
        return Vendor.objects.filter(is_active=True).prefetch_related('branches')


class VendorDetailView(DetailView):
    model = Vendor
    template_name = 'vendors/vendor_detail.html'
    context_object_name = 'vendor'
    
    def get_queryset(self):
        return Vendor.objects.filter(is_active=True).prefetch_related('branches', 'items')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.filter(is_active=True)[:12]
        context['branches'] = self.object.branches.filter(is_active=True)
        return context

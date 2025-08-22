from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Vendor, Branch
from .forms import VendorForm


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


@staff_member_required
def add_vendor(request):
    if request.method == 'POST':
        form = VendorForm(request.POST, request.FILES)
        if form.is_valid():
            vendor = form.save()
            messages.success(request, f'Vendor "{vendor.name}" успешно создан!')
            return redirect('vendors:vendor_list')
    else:
        form = VendorForm()
    return render(request, 'vendors/add_vendor.html', {'form': form})
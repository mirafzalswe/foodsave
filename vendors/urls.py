from django.urls import path
from . import views

app_name = 'vendors'

urlpatterns = [
    path('', views.VendorListView.as_view(), name='vendor_list'),
    path('add/', views.add_vendor, name='add_vendor'),
    path('<int:pk>/', views.VendorDetailView.as_view(), name='vendor_detail'),
]

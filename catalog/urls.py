from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.CatalogView.as_view(), name='catalog'),
    path('map/', views.MapView.as_view(), name='map'),
    path('category/<slug:category_slug>/', views.CategoryView.as_view(), name='category'),
    path('item/<int:pk>/', views.ItemDetailView.as_view(), name='item_detail'),
    path('search/', views.SearchView.as_view(), name='search'),
]

from django.urls import path
from apps.products import views


urlpatterns = [

    # Additional views for the e-commerce application
    path('addProducts/', views.add_products, name='add_product'),
    path('listProducts/', views.list_products, name='list_products'),
    path('addCategory/', views.add_category, name='add_category'),
    path('addTag/', views.add_tags, name='add_tag'),
]

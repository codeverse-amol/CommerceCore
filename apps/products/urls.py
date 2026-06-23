from django.urls import path
from apps.products import views


urlpatterns = [

    # Additional views for the e-commerce application
    # path('addProducts/', views.add_products, name='add_product'),
    # path('addCategory/', views.add_category, name='add_category'),
    # path('addTag/', views.add_tags, name='add_tag'),

    path(
        'listProducts/',
        views.list_products,
        name='list_products'
    ),

    path(
        '<int:id>/',
        views.product_detail,
        name='product_detail'
    ),

    path(
        'review/<int:product_id>/',
        views.add_review,
        name='add_review'
    ),
]

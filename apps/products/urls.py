from django.urls import path
from apps.products import views
from django.conf.urls.static import static
from django.conf import settings



urlpatterns = [

    # Additional views for the e-commerce application
    path('addProducts/', views.add_products, name='add_product'),
    path('listProducts/', views.list_products, name='list_products'),
    path('addCategory/', views.add_category, name='add_category'),
    path('addTag/', views.add_tags, name='add_tag'),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
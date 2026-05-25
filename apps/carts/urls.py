from django.urls import path
from .views import *
from apps.carts import views

from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/remove/<int:cart_item_id>/', views.remove_from_cart, name='remove_cart_item'),

]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
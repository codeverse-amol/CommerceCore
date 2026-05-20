from django.urls import path
from .views import *
from apps.orders import views

from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('order/', views.placed_orders, name='place_order'),
    path('order/success/', views.order_success, name='order_success'),

]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
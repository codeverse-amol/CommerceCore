from django.urls import path
from .views import *
from apps.orders import views

from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('place/', views.placed_orders, name='placed_order'),
    # path('success/', views.order_success, name='order_success'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('<int:order_id>/', views.order_detail, name='order_detail'),
    path('cancel/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('checkout/', views.checkout, name='checkout')
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
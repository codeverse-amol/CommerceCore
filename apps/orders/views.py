from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from apps.orders.models import Order, OrderItem
from apps.carts.views import get_or_create_cart

# Create your views here.


@login_required
def placed_orders(request):
    cart = get_or_create_cart(request.user)
    cart_items = cart.items.all()

    if not cart_items.exists():
        return HttpResponse("Cart is empty")

    order = Order.objects.create(user=request.user)
    total_price = 0

    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity
        )
        total_price += item.product.price * item.quantity
    order.price = total_price
    order.save()
    cart_items.delete()

    return render(request, 'app/order_success.html', {
        'order': order
    })



@login_required
def order_success(request):
    return render(request, 'app/order_success.html')



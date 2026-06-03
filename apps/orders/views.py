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
    cart_items = cart.items.all()   # type: ignore

    if not cart_items.exists():
        return redirect("my_orders")
    
    for item in cart_items:

        if item.quantity > item.product.stock:

            return HttpResponse(
                f"{item.product.name} only has {item.product.stock} items left"
            )
        
    subtotal = sum(item.total_price for item in cart_items)

    order = Order.objects.create(
        user=request.user,
        total_amount=subtotal
    )

    for item in cart_items:

        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price_at_purchase=item.product.price,
            total_price=item.total_price
        )

        item.product.stock -= item.quantity
        item.product.save()
        

    cart_items.delete()

    return render(request, 'orders/order_success.html', {'order': order})



# @login_required
# def order_success(request):
#     return render(request, 'orders/order_success.html')


# my_orders
@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'orders/my_orders.html', {'orders':orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    return render(request, 'orders/order_detail.html', {'order':order})



@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    print(order.status)
    if order.status != 'PENDING':
        return HttpResponse("Only pending orders can be cancelled.")
    

    for item in order.items.all():
        item.product.stock += item.quantity
        item.product.save()
    order.status = 'CANCELLED'
    order.save()
    print("Order cancelled")

    return redirect('my_orders')
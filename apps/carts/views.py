from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from apps.carts.models import CartItem, Product, Cart



# Create your views here.


# get_or_create_cart function retrieves the cart associated with the user. If the cart does not exist, it creates a new cart for the user. This function is useful for managing the user's shopping cart in the application.
def get_or_create_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart



@login_required
def add_to_cart(request, product_id):
    cart = get_or_create_cart(request.user)
    product = get_object_or_404(Product, pk=product_id)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    
    return redirect('view_cart')


@login_required
def view_cart(request):
    cart = get_or_create_cart(request.user)
    cart_items = cart.items.all()       # type: ignore
    subtotal = sum(item.total_price for item in cart_items)


    return render(request, 'carts/cart.html', {'cart_items': cart_items,'subtotal': subtotal})


@login_required
def increase_quantity(request, item_id):
    cart = get_or_create_cart(request.user)
    cart_item = get_object_or_404(CartItem, pk=item_id, cart=cart)

    if cart_item.quantity < cart_item.product.stock:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('view_cart')


@login_required
def decrease_quantity(request, item_id):
    cart = get_or_create_cart(request.user)
    cart_item = get_object_or_404(CartItem, pk=item_id, cart=cart)


    cart_item.quantity -= 1
    if cart_item.quantity <= 0:
        cart_item.delete()
    else:
        cart_item.save()

    return redirect('view_cart')


@login_required
def remove_from_cart(request, cart_item_id):
    cart = get_or_create_cart(request.user)
    cart_item = get_object_or_404(CartItem, pk=cart_item_id, cart=cart)

    if cart_item:
        cart_item.delete()

    return redirect('view_cart')



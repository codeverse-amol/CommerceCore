from celery import shared_task
from django.core.mail import send_mail

from apps.orders.models import Order




@shared_task
def send_order_confirmation_email(order_id):

    order = Order.objects.get(id=order_id)

    subject = f"Order Confirmation - Order #{order.id}"

    message = f"""
            Hello {order.user.username},

            Thank you for your order!

            Order ID: #{order.id}
            Order Status: {order.status}
            Total Amount: ₹{order.total_amount}

            Your order has been successfully placed.

            Thank you for shopping with CommerceCore!
            """

    send_mail(
        subject=subject,
        message=message,
        from_email=None,
        recipient_list=[order.user.email],
    )
    
    print(f"Preparing confirmation email for order #{order_id}")











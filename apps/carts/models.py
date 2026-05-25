from django.db import models
from django.contrib.auth.models import User
from apps.products.models import Product

# Create your models here.


# Cart → OneToOne → User
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')


# Cart → ManyToMany → Product (through CartItem)
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    
    @property
    def total_price(self):
        return self.product.price * self.quantity


from django.db import models
from django.contrib.auth.models import User
from apps.products.models import Product
# Create your models here.



# Order → ManyToOne → User
# Order → ManyToMany → Product (through OrderItem)    
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    price = models.FloatField(default=0)

# OrderItem → ManyToOne → Order
# OrderItem → ManyToOne → Product
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()



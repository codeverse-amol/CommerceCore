from django.db import models
from django.contrib.auth.models import User

# Create your models here.


# Category → OneToMany → Product
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    

# Tag → ManyToMany → Product
class Tag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# Product → ManyToOne → Category
# Product → ManyToMany → Tag
# Product → ManyToOne → User (Seller)
# Product → ManyToMany → Cart
class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    tags = models.ManyToManyField(Tag, related_name='products')
    image = models.ImageField(upload_to='products/', null=True, blank=True)


    def __str__(self):
        return self.name


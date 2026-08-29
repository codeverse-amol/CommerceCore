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
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="products"
    )
    tags = models.ManyToManyField(Tag, related_name="products")
    image = models.ImageField(upload_to="products/", null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    description = models.TextField()
    # seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')

    def __str__(self):
        return self.name


class Review(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.user.username} - {self.product.name}"


class LowStockAlert(models.Model):

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        RESOLVED = "RESOLVED", "Resolved"

    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name="low_stock_alert",
    )

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.ACTIVE
    )

    notified_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    

    def __str__(self):
        return f"{self.product.name} - {self.status}"

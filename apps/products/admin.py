from django.contrib import admin

from apps.products.models import Category, Product, Tag, Review

# Register your models here.


admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Review)



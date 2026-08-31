from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from apps.products.models import Product
from apps.common.cache import invalidate_product_list_cache


@receiver(post_save, sender=Product)
def product_saved(sender, instance, **kwargs):
    invalidate_product_list_cache()


@receiver(post_delete, sender=Product)
def product_deleted(sender, instance, **kwargs):
    invalidate_product_list_cache()
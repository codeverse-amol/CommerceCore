from django.core.cache import cache


def invalidate_product_list_cache():
    cache.delete_pattern("products:list:*")

    print("Product List Cache invalidated")


    
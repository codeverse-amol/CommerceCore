from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db.models import Q, Avg
from django.core.cache import cache

from apps.products.forms import CategoryForm, ProductForm, TagForm, ReviewForm
from apps.products.models import Product, Review

# from django.contrib.auth.models import User

from django.core.paginator import Paginator

# Create your views here.


@login_required
def list_products(request):

    query = request.GET.get("q", "")
    page_number = request.GET.get("page", "1")

    # Different cache key for different searches/pages
    cache_key = f"products:list:q={query}:page={page_number}"

    # --------------------------------------------------
    # Cache HIT
    # --------------------------------------------------

    cached_response = cache.get(cache_key)

    if cached_response is not None:
        print("CACHE HIT:", cache_key)
        return HttpResponse(cached_response)

    # --------------------------------------------------
    # Cache MISS
    # --------------------------------------------------

    print("CACHE MISS:", cache_key)

    products = Product.objects.select_related("category").prefetch_related("tags")

    if query:
        products = products.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(category__name__icontains=query)
            | Q(tags__name__icontains=query)
        ).distinct()

    paginator = Paginator(products, 8)

    page_obj = paginator.get_page(page_number)

    # Render page
    response = render(
        request,
        "products/listProducts.html",
        {
            "products": products,
            "page_obj": page_obj,
        },
    )

    # --------------------------------------------------
    # Store rendered page in Redis
    # --------------------------------------------------

    cache.set(
        cache_key,
        response.content,
        300,  # 5 minutes
    )

    print("CACHE SET:", cache_key)

    return response


def product_detail(request, id):

    product = Product.objects.get(id=id)

    reviews = Review.objects.filter(product=product).select_related("user")

    avg_rating = reviews.aggregate(Avg("rating"))["rating__avg"]
    review_count = reviews.count()

    review_form = ReviewForm()

    context = {
        "product": product,
        "reviews": reviews,
        "avg_rating": avg_rating,
        "review_count": review_count,
        "review_form": review_form,
    }

    return render(request, "products/product_detail.html", context)


@login_required
def add_review(request, product_id):

    product = Product.objects.get(id=product_id)

    if request.method == "POST":

        if Review.objects.filter(product=product, user=request.user).exists():

            return redirect("product_detail", id=product.id)  # type: ignore

        form = ReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user

            review.save()

    return redirect("product_detail", id=product.id)  # type: ignore


# def add_category(request):
#     if request.method=="POST":
#         form = CategoryForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('dashboard')
#     else:
#         form = CategoryForm()
#     return render(request, "products/addCategory.html", {'form':form})


# def add_tags(request):
#     if request.method=="POST":
#         form = TagForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('dashboard')
#     else:
#         form = TagForm()
#     return render(request, "products/addTags.html", {'form':form})


# def add_products(request):

#     if request.method == "POST":
#         form = ProductForm(request.POST)

#         if form.is_valid():

#             product = form.save(commit=False)
#             product.user = request.user
#             product.save()
#             form.save_m2m()

#             return redirect('list_products')

#     else:
#         form = ProductForm()

#     return render(request, "products/addProducts.html", {'form': form})

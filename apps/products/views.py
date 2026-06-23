from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db.models import Q, Avg


from apps.products.forms import CategoryForm, ProductForm, TagForm, ReviewForm
from apps.products.models import Product, Review
# from django.contrib.auth.models import User

from django.core.paginator import Paginator

# Create your views here.




@login_required
def list_products(request):
    query = request.GET.get('q')
    products = Product.objects.select_related("category").prefetch_related("tags")

    # Q objects allow us to perform complex queries with OR conditions. 
    # In this case, we are filtering products based on whether the query string is contained in the product's name, description, category name, or tag names. 
    # The distinct() method is used to ensure that we don't get duplicate products in the results when a product matches multiple conditions.

    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()

    paginator = Paginator(products, 8)

    page_number = request.GET.get('page')

    page_obj = paginator.get_page(page_number)

    return render(request, "products/listProducts.html", {'products':products, 'page_obj':page_obj})




def product_detail(request, id):

    product = Product.objects.get(id=id)

    reviews = Review.objects.filter(product=product).select_related('user')

    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    review_count = reviews.count()

    review_form = ReviewForm()

    context = {
        'product': product,
        'reviews': reviews,
        'avg_rating': avg_rating,
        "review_count": review_count,
        'review_form': review_form,
    }


    return render(request, 'products/product_detail.html', context)



@login_required
def add_review(request, product_id):

    product = Product.objects.get(id=product_id)

    if request.method == "POST":

        if Review.objects.filter(product=product, user=request.user).exists():

            return redirect("product_detail", id=product.id)

        form = ReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user

            review.save()

    return redirect("product_detail", id=product.id)











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


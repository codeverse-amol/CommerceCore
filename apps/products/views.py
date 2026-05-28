from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db.models import Q


from apps.products.forms import CategoryForm, ProductForm, TagForm
from apps.products.models import Product
# from django.contrib.auth.models import User

# Create your views here.


@login_required
def add_category(request):
    if request.method=="POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = CategoryForm()
    return render(request, "products/addCategory.html", {'form':form})


@login_required
def add_tags(request):
    if request.method=="POST":
        form = TagForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = TagForm()
    return render(request, "products/addTags.html", {'form':form})


@login_required
def add_products(request):

    if request.method == "POST":
        form = ProductForm(request.POST)

        if form.is_valid():

            product = form.save(commit=False)
            product.user = request.user
            product.save()
            form.save_m2m()

            return redirect('list_products')

    else:
        form = ProductForm()

    return render(request, "products/addProducts.html", {'form': form})



@login_required
def list_products(request):
    query = request.GET.get('q')
    products = Product.objects.select_related("category").prefetch_related("tags")

    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()

    # Q objects allow us to perform complex queries with OR conditions. In this case, we are filtering products based on whether the query string is contained in the product's name, description, category name, or tag names. The distinct() method is used to ensure that we don't get duplicate products in the results when a product matches multiple conditions.

    else:
        products = Product.objects.all()
        
    return render(request, "products/listProducts.html", {'products':products})




def product_detail(request, id):

    product = Product.objects.get(id=id)

    return render(
        request,
        'products/product_detail.html',
        {'product': product}
    )
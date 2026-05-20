from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
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
    return render(request, "app/addCategory.html", {'form':form})


@login_required
def add_tags(request):
    if request.method=="POST":
        form = TagForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = TagForm()
    return render(request, "app/addTags.html", {'form':form})


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

    return render(request, "app/addProducts.html", {'form': form})



@login_required
def list_products(request):
    products = Product.objects.select_related("category").prefetch_related("tags")
    return render(request, "app/listProducts.html", {'products':products})

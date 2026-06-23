from django import forms
from .models import Category, Product, Tag, Review
from django.contrib.auth.models import User



class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name"]


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ["name"]


class ProductForm(forms.ModelForm):
    category = forms.ModelChoiceField(
    queryset=Category.objects.all(),
    empty_label="Select Category"   # removes "--------"
)
    class Meta:
        model = Product
        fields = ['name', 'price', 'category', 'tags']



class ReviewForm(forms.ModelForm):

    class Meta:
        model = Review
        fields = ['rating', 'comment']





# User → Django View → ORM → SQL → MySQL → Data → ORM → View → Template
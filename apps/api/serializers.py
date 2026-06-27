from rest_framework import serializers
from apps.products.models import Product, Category, Tag

class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
        ]

class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = [
            "id",
            "name",
        ]

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    category_id = serializers.PrimaryKeyRelatedField(
        queryset = Category.objects.all(),
        source = "category",
        write_only=True
    )

    tags = TagSerializer(many=True, read_only=True)


    class Meta:
        model = Product
        # fields = "__all__"
        fields = [
            "id",
            "name",
            "price",
            "stock",
            "category",
            "category_id",
            "tags",
        ]
        

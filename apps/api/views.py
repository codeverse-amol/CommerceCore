from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from apps.products.models import Product
from apps.api.serializers import ProductSerializer

from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView

from rest_framework.viewsets import ModelViewSet

# Create your views here.



class ProductViewSet(ModelViewSet):

    queryset = Product.objects.all()

    serializer_class = ProductSerializer

    permission_classes = [IsAuthenticated]














# class ProductListAPIView(ListAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer



# class ProductDetailAPIView(RetrieveAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer


# class ProductCreateAPIView(CreateAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer

# class ProductUpdateAPIView(UpdateAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer

# class ProductDestroyAPIView(DestroyAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer



# | Generic View      | HTTP Method    | Purpose                |
# | ----------------- | -------------- | ---------------------- |
# | `ListAPIView`     | `GET`          | Get all records        |
# | `RetrieveAPIView` | `GET`          | Get one record         |
# | `CreateAPIView`   | `POST`         | Create new record      |
# | `UpdateAPIView`   | `PUT`, `PATCH` | Update existing record |
# | `DestroyAPIView`  | `DELETE`       | Delete record          |






# class ProductGenericAPIView(GenericAPIView):

#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer

#     def get(self, request):

#         serializer = self.get_serializer(self.get_queryset(), many=True)

#         return Response(serializer.data)
    






# class ProductListAPIView(APIView):

#     def get(self, request):
#         products = Product.objects.all()
#         serializer = ProductSerializer(products, many=True)

#         return Response(serializer.data, status=200)
    

# class HelloAPIView(APIView):
#     def get(self, request):
#         return Response({
#             "message": "Hello from APIView",
#             "framework": "Django REST Framework"
#         })
    




from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.viewsets import ModelViewSet

from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser, IsAuthenticatedOrReadOnly
from .permissions import ReadOnlyPermission, OnlyPostPermission

from apps.products.models import Product
from apps.api.serializers import ProductSerializer

from .pagination import ProductPagination
from .pagination import ProductLimitOffsetPagination
from .pagination import ProductCursorPagination
# Create your views here.



class ProductViewSet(ModelViewSet):

    queryset = Product.objects.all()

    serializer_class = ProductSerializer

    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]
    # permission_classes = [IsAdminUser]
    # permission_classes = [IsAuthenticatedOrReadOnly]

    # permission_classes = [ReadOnlyPermission]
    # permission_classes = [OnlyPostPermission]

    # pagination_class = ProductPagination
    # pagination_class = ProductLimitOffsetPagination
    pagination_class = ProductCursorPagination






    

'''
Difference between IsAuthenticated and IsAdminUser?

| IsAuthenticated                  | IsAdminUser                                    |
| -------------------------------- | ---------------------------------------------- |
| User must be logged in           | User must be logged in **and** `is_staff=True` |
| Any authenticated user           | Only admin/staff users                         |
| Returns 401 if not authenticated | Returns 403 if authenticated but not staff     |

'''








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
    




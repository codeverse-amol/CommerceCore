from django.urls import path
from rest_framework.routers import DefaultRouter

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import ProductViewSet

router = DefaultRouter()

router.register(
    r"products",
    ProductViewSet,
    basename="products",
)

urlpatterns = [
    path(
        "token/",
        TokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),

    path(
        "token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),
]

# append router urls
urlpatterns += router.urls










































# from .views import ProductListAPIView, HelloAPIView, ProductGenericAPIView
# from .views import ProductListAPIView, ProductDetailAPIView, ProductCreateAPIView, ProductUpdateAPIView, ProductDestroyAPIView



# urlpatterns = [

    # path(
    #     "products/",
    #     ProductListAPIView.as_view(),
    #     name="api-products",
    # ),


    # path("hello/", HelloAPIView.as_view(), name="hello-api"),

    # path("products_generic/", ProductGenericAPIView.as_view(), name="products-generic"),

#     path(
#     "products/<int:pk>/",
#     ProductDetailAPIView.as_view(),
#     name="product-detail-api",
# ),

#     path(
#     "products/create/",
#     ProductCreateAPIView.as_view(),
#     name="product-detail-api",
# ),

#     path(
#     "products/<int:pk>/update/",
#     ProductUpdateAPIView.as_view(),
#     name="product-detail-api",
# ),

#     path(
#     "products/<int:pk>/delete/",
#     ProductDestroyAPIView.as_view(),
#     name="product-detail-api",
# ),
# ]


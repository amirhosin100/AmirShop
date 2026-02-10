import time

from rest_framework import views, status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters import rest_framework as filters
from core.cache.ttl import CacheTTL
from apps.product.services import ProductService
from apps.product.models import Product
from apps.product.serializer.user_serializer import (
    ProductSimpleSerializer
)
from apps.product.serializer.common_seializer import (
    ProductDetailSerializer,
)
from apps.product.filters import ProductFilter


class ProductListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductSimpleSerializer
    queryset = Product.objects.all()
    pagination_class = PageNumberPagination
    page_size = 10

    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ProductFilter

    @method_decorator(cache_page(CacheTTL.PRODUCT_LIST, key_prefix='product:list'))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        time.sleep(2)
        return super().get_queryset()


class ProductDetailView(views.APIView):
    serializer_class = ProductDetailSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, product_id):
        data = ProductService.load_product_detail(product_id)
        if not data:
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return Response(
                    data={
                        "message": f"Product with id {product_id} does not exist",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
            serializer = ProductDetailSerializer(product, many=False)
            data = serializer.data

            ProductService.save_product_detail(data, product_id)

        return Response(
            data,
            status=status.HTTP_200_OK,
        )

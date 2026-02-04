from django.contrib.admin.templatetags.admin_list import pagination
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from rest_framework import views, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.product.services import ProductService
from apps.product.models import Product
from apps.product.serializer.user_serializer import (
    ProductSimpleSerializer
)
from apps.product.serializer.common_seializer import (
    ProductDetailSerializer,
)


class ProductListView(views.APIView):
    serializer_class = ProductSimpleSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        page = request.GET.get("page", 1)
        q = request.GET.get("q", "")

        data = ProductService.load_product_list(page, q)

        # if data didn't exist in cache
        if not data:
            query = Product.objects.all()
            if q:
                query = query.filter(name__icontains=q)

            paginator = Paginator(query, 10)

            try:
                products = paginator.page(page)
            except PageNotAnInteger:
                return Response(
                    data={
                        "error": "page is not an integer",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            except EmptyPage:
                return Response(
                    data={
                        "error": "page is empty",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            serializer = ProductDetailSerializer(products, many=True)
            data = {
                "page": page,
                "count": paginator.num_pages,
                "data": serializer.data,
            }
            ProductService.save_product_list(data, page, q)

        return Response(
            data,
            status=status.HTTP_200_OK,
        )


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

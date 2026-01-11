from rest_framework import views, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
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
        queryset = Product.objects.all()

        if q := request.GET.get('q'):
            # TODO use postgresql search
            queryset = queryset.filter(name__icontains=q)

        serializer = ProductSimpleSerializer(queryset, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class ProductDetailView(views.APIView):
    serializer_class = ProductDetailSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                data={
                    "message": f"Product with id {product_id} does not exist",
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProductDetailSerializer(product)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

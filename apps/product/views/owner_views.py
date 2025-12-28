from rest_framework import views, status
from rest_framework.permissions import IsAuthenticated
from permissions.product import IsProductOwner
from permissions.market import IsMarketOwner, IsMarketer
from rest_framework.response import Response
from apps.market.models import Market
from apps.product.serializer.owner_serializer import (
    ProductOwnerCreateSerializer,
    ProductOwnerUpdateSerializer,
)
from apps.product.serializer.common_seializer import (
    ProductDetailSerializer, ProductImageSerializer, ProductFeatureSerializer,
)
from apps.product.models import (
    Product,
    ProductImage,
    ProductFeature,
)


class ProductCreateView(views.APIView):
    serializer_class = ProductOwnerCreateSerializer
    permission_classes = (IsAuthenticated, IsMarketOwner)

    def post(self, request, market_id):
        market = Market.objects.get(id=market_id)

        self.check_object_permissions(request, market)

        serializer = self.serializer_class(data=request.data)

        serializer.is_valid(raise_exception=True)

        serializer.create(serializer.validated_data)

        return Response(
            data=serializer.data,
            status=status.HTTP_201_CREATED
        )


class ProductUpdateView(views.APIView):
    serializer_class = ProductOwnerUpdateSerializer
    permission_classes = (IsAuthenticated, IsProductOwner)

    def patch(self, request, product_id):
        product = Product.objects.get(id=product_id)

        self.check_object_permissions(request, product)

        serializer = self.serializer_class(instance=product, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)

        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )


class ProductDeleteView(views.APIView):
    permission_classes = (IsAuthenticated, IsProductOwner)

    def delete(self, request, product_id):
        product = Product.objects.get(id=product_id)

        self.check_object_permissions(request, product)

        product.delete()

        return Response(
            data={
                "message": f"product by id {product.id} deleted!",
            },
            status=status.HTTP_200_OK
        )


class ProductDetailView(views.APIView):
    """
    this view shows product detail for owner
    """

    serializer_class = ProductDetailSerializer
    permission_classes = (IsAuthenticated, IsProductOwner)

    def get(self, request, product_id):
        product = Market.objects.get(id=product_id)

        self.check_object_permissions(request, product)

        serializer = self.serializer_class(instance=product)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class ProductListView(views.APIView):
    """
    this view shows marketer's products
    """

    permission_classes = (IsAuthenticated, IsMarketer)
    serializer_class = ProductDetailSerializer

    def get(self, request):
        self.check_permissions(request)

        products = Product.objects.filter(market__marketer__user=request.user)

        serializer = ProductDetailSerializer(products, many=True)

        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK,
        )


class ProductImageCreateView(views.APIView):
    """
    this view create an image for product
    """
    permission_classes = (IsAuthenticated, IsProductOwner)
    serializer_class = ProductImageSerializer

    def post(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)

        except Product.DoesNotExist:
            return Response(
                data={
                    "message": "product not found!"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        self.check_object_permissions(request, product)

        serializer = ProductImageSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        serializer.save(product=product)

        return Response(
            data=serializer.data,
            status=status.HTTP_201_CREATED
        )


class ProductImageUpdateView(views.APIView):
    permission_classes = (IsAuthenticated, IsProductOwner)
    serializer_class = ProductImageSerializer

    def patch(self, request, product_id, image_id):

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                data={
                    "message": "product not found!"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        self.check_object_permissions(request, product)

        try:
            image = ProductImage.objects.filter(product_id=product_id).get(id=image_id)
        except ProductImage.DoesNotExist:
            return Response(
                data={
                    "message": "image not found!"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProductImageSerializer(
            instance=image,
            data=request.data,
            partial=True
        )

        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )


class ProductImageDeleteView(views.APIView):
    permission_classes = (IsAuthenticated, IsProductOwner)
    serializer_class = ProductImageSerializer

    def delete(self, request, product_id, image_id):

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                data={
                    "message": "product not found!"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        self.check_object_permissions(request, product)

        try:
            image = ProductImage.objects.filter(product_id=product_id).get(id=image_id)
        except ProductImage.DoesNotExist:
            return Response(
                data={
                    "message": "image not found!"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        image.delete()

        return Response(
            data={
                "message": f"image by id {image.id} deleted!",
            },
            status=status.HTTP_200_OK
        )


class ProductFeatureCreateView(views.APIView):
    permission_classes = (IsAuthenticated, IsProductOwner)
    serializer_class = ProductFeatureSerializer

    def post(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                data={
                    "message": "product not found!"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        self.check_object_permissions(request, product)

        serializer = ProductFeatureSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        serializer.save(product=product)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )


class ProductFeatureUpdateView(views.APIView):
    permission_classes = (IsAuthenticated, IsProductOwner)
    serializer_class = ProductFeatureSerializer

    def patch(self, request, product_id, feature_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                data={
                    "message": "product not found!"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        self.check_object_permissions(request, product)

        try:
            feature = ProductFeature.objects.filter(product_id=product_id).get(id=feature_id)
        except ProductFeature.DoesNotExist:
            return Response(
                data={
                    "message": "feature not found!"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProductFeatureSerializer(
            instance=feature,
            data=request.data,
            partial=True
        )

        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )


class ProductFeatureDeleteView(views.APIView):
    permission_classes = (IsAuthenticated, IsProductOwner)
    serializer_class = ProductFeatureSerializer

    def delete(self, request, product_id, feature_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                data={
                    "message": "product not found!"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        self.check_object_permissions(request, product)

        try:
            feature = ProductFeature.objects.filter(product_id=product_id).get(id=feature_id)
        except ProductFeature.DoesNotExist:
            return Response(
                data={
                    "message": "feature not found!"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        feature.delete()

        return Response(
            data={
                "message": f"feature by id {feature.id} deleted!",
            },
            status=status.HTTP_200_OK
        )

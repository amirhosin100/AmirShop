import logging
from rest_framework import views, status, generics
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.cart.serializer.user_serializer import (
    CartSerializer,
    CartItemSerializer,
    CartInfoDetailSerializer
)
from apps.cart.models import (
    Cart,
    CartInfo
)
from apps.product.models import Product

logger = logging.getLogger(__name__)


class CartDetailView(views.APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CartSerializer

    def get(self, request):
        cart = Cart.manage_items.get_cart(request.user)

        serializer = CartSerializer(instance=cart)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class AddToCartView(views.APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CartItemSerializer

    def post(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            logger.info('Product does not exist')
            return Response(
                data={
                    "message": "Product does not exist",
                },
                status=status.HTTP_404_NOT_FOUND
            )

        item = Cart.manage_items.add(request.user, product)

        serializer = CartItemSerializer(instance=item)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )


class DecreaseCartItemView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            logger.info('Product does not exist')
            return Response(
                data={
                    "message": "Product does not exist",
                },
                status=status.HTTP_404_NOT_FOUND
            )
        try:
            item = Cart.manage_items.decrease(request.user, product)
        except ValueError:
            logger.info(f"This product don't exist in your cart. Cart id is {request.user.cart.id}")
            return Response(
                data={
                    "message": "This product don't exist in your cart",
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = CartItemSerializer(instance=item)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class SetItemQuantityView(views.APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CartItemSerializer

    def post(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                data={
                    "message": "Product does not exist",
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CartItemSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        if not serializer.validated_data.get('quantity'):
            logger.warning('quantity is empty')
            return Response(
                data={
                    "error": "quantity is required",
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        item = Cart.manage_items.set(
            request.user,
            product=product,
            quantity=serializer.validated_data.get('quantity'),
        )
        serializer = CartItemSerializer(instance=item)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class RemoveCartItemView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                data={
                    "message": "Product does not exist",
                },
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            Cart.manage_items.remove(request.user, product)
        except ValueError as e:
            return Response(
                data={
                    "message": "product doesn't exist in your cart",
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        logger.info(f'Product deleted from cart. Product id is {product.id}')

        return Response(
            data={
                "message": "product has been removed",
            },
            status=status.HTTP_200_OK
        )


class CartClearView(views.APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CartSerializer

    @extend_schema(
        responses={
            status.HTTP_200_OK: CartItemSerializer,
        },
        request=None
    )
    def post(self, request):
        cart = Cart.manage_items.clear(request.user)

        serializer = CartSerializer(instance=cart)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class CartInfoListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CartInfoDetailSerializer

    def get_queryset(self):
        queryset = CartInfo.objects.filter(user=self.request.user)
        return queryset


class CartInfoDetailView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CartInfoDetailSerializer

    def get_queryset(self):
        queryset = CartInfo.objects.filter(user=self.request.user)
        return queryset

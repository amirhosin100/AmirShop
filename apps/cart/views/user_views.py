from rest_framework import views, status
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.cart.serializer.user_serializer import (
    CartSerializer,
    CartItemSerializer,
)
from apps.cart.models import (
    Cart,
)
from apps.product.models import Product


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
            return Response(
                data={
                    "message": "Product does not exist",
                },
                status=status.HTTP_404_NOT_FOUND
            )

        quantity = request.data.get("quantity")

        if isinstance(quantity, int):
            if quantity <= 0:
                return Response(
                    data={
                        "message": "Quantity must be greater than 0",
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        if quantity is None:
            item = Cart.manage_items.add(request.user, product)
        else:
            item = Cart.manage_items.set(request.user, product, quantity=quantity)

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
            return Response(
                data={
                    "message": "Product does not exist",
                },
                status=status.HTTP_404_NOT_FOUND
            )
        try:
            item = Cart.manage_items.decrease(request.user, product)
        except ValueError:
            return Response(
                data={
                    "message": "product don't exist to cart",
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

        item = Cart.manage_items.set(
            request.user,
            product=product,
            quantity=serializer.validated_data["quantity"]
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
                    "message": "product doesn't exist to cart",
                },
                status=status.HTTP_400_BAD_REQUEST
            )

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

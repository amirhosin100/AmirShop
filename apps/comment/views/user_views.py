from rest_framework import views, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.comment.models import Comment
from apps.comment.serializers.user_serializer import (
    CommentImageSerializer,
    CommentSerializer,
)
from apps.product.models import Product


class CommentCreateView(views.APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CommentSerializer

    def post(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                data={
                    'error': f'product with id {product_id} does not exist'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CommentSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(product=product, user=request.user)

        return Response(
            data=serializer.data,
            status=status.HTTP_201_CREATED
        )


class CommentImageCreateView(views.APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CommentImageSerializer

    def post(self, request, comment_id):
        try:
            comment = Comment.objects.filter(user=request.user).get(id=comment_id)
        except Comment.DoesNotExist:
            return Response(
                data={
                    'error': f"comment with id {comment_id} does not exist"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CommentImageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(comment=comment, user=request.user)

        return Response(
            data=serializer.data,
            status=status.HTTP_201_CREATED
        )

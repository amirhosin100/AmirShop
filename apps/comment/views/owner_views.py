from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics, status
from apps.comment.models import Comment
from apps.comment.serializers.owner_serializer import (
    CommentDetailSerializer,
)


class CommentListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CommentDetailSerializer

    def get_queryset(self):
        queryset = Comment.objects.filter(product__market__marketer__user=self.request.user)
        return queryset


class CommentDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CommentDetailSerializer
    lookup_field = 'comment_id'

    def retrieve(self, request, *args, **kwargs):

        try:
            query = Comment.objects.filter(
                product__market__marketer__user=request.user,
            )

            comment = query.get(id=str(kwargs[self.lookup_field]))
        except Comment.DoesNotExist:
            return Response(
                data={
                    'error': f'Comment with {kwargs[self.lookup_field]} does not exist'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CommentDetailSerializer(instance=comment)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

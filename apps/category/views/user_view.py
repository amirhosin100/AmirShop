from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.category.models import Category
from apps.category.serializer.user_serializer import (
    CategoryDetailSerializer,
    CategoryListSerializer
)


class CategoryListView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CategoryListSerializer

    def get(self, request):
        categories = Category.objects.all()

        serializer = CategoryListSerializer(categories, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class CategoryDetailView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CategoryDetailSerializer

    def get(self,request,category_id):
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response(
                data={
                    "error" : f"category with {category_id} does not exist"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CategoryDetailSerializer(category)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )




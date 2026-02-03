from rest_framework import serializers

from apps.category.models import (
    Category,
    SubCategory
)


class SubCategoryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = (
            "title",
            "id"
        )


class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            "title",
            "id",
        )


class CategoryDetailSerializer(serializers.ModelSerializer):
    sub_categories = SubCategoryDetailSerializer(many=True, read_only=True)
    class Meta:
        model = Category
        fields = (
            "title",
            "description",
            "id",
            "sub_categories"
        )



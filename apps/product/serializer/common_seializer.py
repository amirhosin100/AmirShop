from unicodedata import category

from rest_framework import serializers

from apps.comment.models import Comment
from apps.comment.serializers.user_serializer import CommentSerializer
from apps.product.models import (
    ProductImage,
    ProductFeature,
    Product,
)


class ProductImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField(read_only=True)
    image = serializers.ImageField(write_only=True)

    class Meta:
        model = ProductImage
        fields = [
            "image",
            "title",
            "url",
            'id'
        ]
        read_only_fields = ['id']

    def get_url(self, image_object):
        return image_object.image.url


class ProductFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductFeature
        fields = [
            "key",
            "value",
            "id",
        ]
        read_only_fields = ['id']


class ProductDetailSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    features = ProductFeatureSerializer(many=True, read_only=True)
    comments = serializers.SerializerMethodField()
    main_category = serializers.SerializerMethodField()
    main_category_id = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    category_id = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "price",
            "discount_price",
            "percentage_off",
            "description",
            "images",
            "features",
            "comments",
            "stock",
            "main_category",
            "main_category_id",
            "category",
            "category_id",
        ]
        read_only_fields = ['id']

    def get_comments(self, obj):
        comments = Comment.published.filter(product_id=obj.id)
        serializer = CommentSerializer(comments, many=True, read_only=True)
        return serializer.data

    def get_category(self, obj):
        return obj.category.title

    def get_category_id(self, obj):
        return obj.category.id

    def get_main_category(self, obj):
        return obj.category.category.title

    def get_main_category_id(self, obj):
        return obj.category.category.id

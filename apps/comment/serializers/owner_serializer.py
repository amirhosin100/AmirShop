from rest_framework import serializers
from apps.comment.models import Comment, CommentImage


class CommentImageDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentImage
        fields = [
            'id',
            'image'
        ]
        read_only_fields = ['image', 'id']


class CommentDetailSerializer(serializers.ModelSerializer):
    images = CommentImageDetailSerializer(read_only=True, many=True)
    user_name = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            'id',
            'user',
            'user_name',
            'product',
            'product_name',
            'content',
            'images',
            'score',
            'status',
        ]

    def get_user_name(self, obj):
        name = obj.user.get_full_name()
        return name if name else "Unknown"

    def get_product_name(self, obj):
        return obj.product.name

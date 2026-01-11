from rest_framework import serializers
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
    images = ProductImageSerializer(many=True,read_only=True)
    features = ProductFeatureSerializer(many=True,read_only=True)

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
            "stock",
        ]
        read_only_fields = ['id']
from rest_framework import serializers
from apps.product.models import (
    Product,
    ProductImage,
    ProductFeature
)
from apps.product.serializer.common_seializer import (
    ProductImageSerializer,
    ProductFeatureSerializer
)


class ProductSimpleSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'name',
            'price',
            'discount_price',
            'percentage_off',
            'description',
            'image',
            'id'
        ]

    # show just first image
    def get_image(self, image_object):
        image = image_object.images.first()
        return ProductImageSerializer(image).data




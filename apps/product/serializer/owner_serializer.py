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


class ProductOwnerCreateSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, required=False)
    features = ProductFeatureSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = [
            "market",
            "name",
            "description",
            "price",
            "percentage_off",
            "discount_price",
            "stock",
            "images",
            "features",
            "updated_at",
            "id",
        ]
        extra_kwargs = {
            "market": {"read_only": True},
        }

    def validate_name(self, name):
        if len(name) < 2:
            raise serializers.ValidationError("product name must be at least 3 characters")
        return name

    def validate_price(self, price):
        if price == 0:
            raise serializers.ValidationError("product price must be greater than 0")
        return price

    def create(self, validated_data):
        images_data = validated_data.pop("images")
        features_data = validated_data.pop("features")

        product = Product.objects.create(**validated_data)

        # crate images
        for image_data in images_data:
            ProductImage.objects.create(product=product, **image_data)

        # crate features
        for feature_data in features_data:
            ProductFeature.objects.create(product=product, **feature_data)


class ProductOwnerUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "name",
            "description",
            "price",
            "percentage_off",
            "discount_price",
            "stock",
            "updated_at",
            "id",
        ]

    def validate_name(self, name):
        if len(name) < 2:
            raise serializers.ValidationError("product name must be at least 3 characters")
        return name

    def validate_price(self, price):
        if price == 0:
            raise serializers.ValidationError("product price must be greater than 0")
        return price


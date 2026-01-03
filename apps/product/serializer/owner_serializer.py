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
    images = ProductImageSerializer(many=True,default=[])
    features = ProductFeatureSerializer(many=True,default=[])

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
        read_only_fields = ['id','market','created_at','updated_at']

    def validate_name(self, name):
        if len(name) < 2:
            raise serializers.ValidationError("product name must be at least 3 characters")
        return name

    def validate_price(self, price):
        if price == 0:
            raise serializers.ValidationError("product price must be greater than 0")
        return price

    def create(self, validated_data,market_id,*args,**kwargs):
        images_data = validated_data.pop("images")
        features_data = validated_data.pop("features")

        product = Product.objects.create(
            market_id=market_id,
            name=validated_data.get("name"),
            description=validated_data.get("description"),
            price=validated_data.get("price"),
            percentage_off=validated_data.get("percentage_off"),
            discount_price=validated_data.get("discount_price"),
            stock=validated_data.get("stock"),

        )

        # create images

        for image_data in images_data:
            ProductImage.objects.create(product=product, **image_data)

        # create features
        for feature_data in features_data:
            ProductFeature.objects.create(product=product, **feature_data)

        return product


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
        read_only_fields = ['id']

    def validate_name(self, name):
        if len(name) < 2:
            raise serializers.ValidationError("product name must be at least 3 characters")
        return name

    def validate_price(self, price):
        if price == 0:
            raise serializers.ValidationError("product price must be greater than 0")
        return price


from rest_framework import serializers
from apps.cart.models import (
    Cart,
    CartItem,
    CartInfo
)


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = (
            'product',
            'product_name',
            'quantity',
            'final_price',
            'id'
        )
        read_only_fields = (
            'product',
            'product_name',
            'final_price',
            'id'
        )

    def get_product_name(self, obj):
        return obj.product.name

    def validate_quantity(self, quantity):
        if not isinstance(quantity, int):
            raise serializers.ValidationError('quantity must be an integer')
        if quantity <= 0:
            raise serializers.ValidationError('Quantity must be positive')
        return quantity


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True)

    class Meta:
        model = Cart
        fields = (
            'items',
            'id',
            'amount'
        )
        read_only_fields = (
            'id',
            'amount',
            'items'
        )


class CartInfoDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartInfo
        fields = (
            'id',
            'amount',
            'items',
            'created_at',
            'status',
        )

from rest_framework import serializers
from apps.market.models import Market


class MarketOwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Market
        exclude = (
            'marketer',
        )
        read_only_fields = ['id','created_at','updated_at']

    def validate_name(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Market name must be at least 4 characters")
        return value

class MarketUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Market
        exclude = (
            'is_active',
            'updated_at',
        )
        read_only_fields = ['id','created_at']

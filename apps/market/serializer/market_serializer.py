from rest_framework import serializers
from apps.market.models import Market


class MarketOwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Market
        exclude = (
            'marketer',
        )

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

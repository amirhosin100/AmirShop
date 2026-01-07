from rest_framework import serializers
from apps.market_request.models import MarketRequest
from utils.validate import check_phone


class MarketRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketRequest
        fields = (
            'mobile_number',
            'age',
            'city',
            'national_code',
            'province',
            'description',
            'address',
            'id',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate_mobile_number(self, mobile_number):
        success,message = check_phone(mobile_number)

        if success:
            return mobile_number
        else:
            raise serializers.ValidationError(message)

    def validate_city(self, city):
        if len(city) <= 1:
            raise serializers.ValidationError("city must be at least 2 characters")

        return city

    def validate_description(self,description):
        if len(description) < 100:
            raise serializers.ValidationError("description must be at least 100 characters")

        return description

    def validate_address(self,address):
        if len(address) < 30:
            raise serializers.ValidationError("address must be at least 30 characters")

        return address

    def validate_national_code(self,national_code):
        if len(national_code) != 10:
            raise serializers.ValidationError("national_code must be at least 10 characters")

        return national_code
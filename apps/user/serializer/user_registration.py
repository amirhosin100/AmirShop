from rest_framework import serializers
from apps.user.models import User


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'phone',
        ]

    def validate_phone(self, phone):
        if not phone.isdigit():
            raise serializers.ValidationError("phone must be a number")

        if len(phone) != 11:
            raise serializers.ValidationError("phone is not valid")

        if not phone.startswith("09"):
            raise serializers.ValidationError("phone must start with <09>")

        return phone

class UserSetPasswordSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True,
        required=True,
    )

    password2 = serializers.CharField(
        write_only=True,
        required=True,
    )

    class Meta:
        model = User
        fields = [
            'phone',
        ]

    def validate(self, data):
        password = data.get("password")
        password2 = data.get("password2")
        if password != password2:
            raise serializers.ValidationError("password and password_repat must be equal")

    def update(self, instance,validated_data):
        password = validated_data.pop("password")
        instance.set_password(password)
        instance.save()

class UserChangeInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
            'bio',
            'photo',
        ]




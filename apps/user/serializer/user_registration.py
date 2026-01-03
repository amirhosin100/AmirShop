from rest_framework import serializers
from apps.user.models import User
from utils.validate import check_phone


class UserRegisterSerializer(serializers.Serializer):
    phone = serializers.CharField(
        required=True,
        max_length=11,
    )

    def validate_phone(self, phone):

        success, message = check_phone(phone)

        if success:
            return phone
        else:
            raise serializers.ValidationError(message)


class UserSetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
    )

    password2 = serializers.CharField(
        write_only=True,
        required=True,
    )

    def validate(self, data):
        password = data.get("password")
        password2 = data.get("password2")
        if password != password2:
            raise serializers.ValidationError("password and password_repat must be equal")
        return data

    def update(self, instance, validated_data):
        password = validated_data.pop("password")
        instance.set_password(password)
        instance.save()


class UserInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
            'bio',
            'photo',
        ]

from rest_framework import test, serializers
from unittest.mock import patch

from apps.user.models import User
from apps.user.serializer.user_registration import (
    UserRegisterSerializer,
    UserSetPasswordSerializer,
)



class UserRegisterSerializerTest(test.APITestCase):

    @patch('apps.user.serializer.user_registration.check_phone')
    def test_check_phone_called(self,mock_check_phone):
        mock_check_phone.return_value = [True,""]
        self.serializer = UserRegisterSerializer(
            data={
                'phone': '09123456789'
            }
        )
        self.serializer.is_valid()
        mock_check_phone.assert_called_once()


class UserSetPasswordSerializerTest(test.APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            phone='09123456789'
        )
        self.user.set_unusable_password()
        self.user.save()

    def test_password_not_equal(self):
        self.serializer = UserSetPasswordSerializer(
            data={
                'password': '1234',
                'password2': '4321',
            }
        )
        with self.assertRaises(serializers.ValidationError):
            self.serializer.is_valid(raise_exception=True)

    def test_update_password(self):
        self.serializer = UserSetPasswordSerializer(
            data={
                'password': '1234',
                'password2': '1234',
            }
        )
        self.serializer.is_valid()
        self.serializer.update(
            instance=self.user,
            validated_data=self.serializer.validated_data
        )
        self.user.refresh_from_db()
        self.assertTrue(self.user.has_usable_password())
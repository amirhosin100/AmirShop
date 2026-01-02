from django.contrib.auth.models import AnonymousUser
from rest_framework import test, status
from rest_framework.test import APIRequestFactory, force_authenticate, APIClient
from django.urls import reverse
from apps.user.models import User
from rest_framework.authtoken.models import Token

from apps.user.views.user_registration_view import (
    UserSetPasswordView
)


class UserCreateCodeTest(test.APITestCase):

    def test_correct_response(self):
        response = self.client.post(
            reverse('user_registration:register'),
            data={
                'phone': '09133333333'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(response.data["mobile_number"], "09133333333")

    def test_user_without_phone(self):
        response = self.client.post(
            reverse('user_registration:register'),
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('This field is required.', str(response.data['phone'][0]))

    def test_phone_not_digit(self):
        response = self.client.post(
            reverse('user_registration:register'),
            data={
                'phone': '0913333333a'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual('phone must be a number', str(response.data['phone'][0]))

    def test_phone_not_equal_length(self):
        response = self.client.post(
            reverse('user_registration:register'),
            data={
                'phone': '09133333'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual('phone is not valid', str(response.data['phone'][0]))

    def test_phone_dont_start_with_zero_nine(self):
        response = self.client.post(
            reverse('user_registration:register'),
            data={
                'phone': '12345678900'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual('phone must start with <09>', str(response.data['phone'][0]))


class UserVerifyCodeTest(test.APITestCase):
    phone_number = "09123456789"

    def setUp(self):
        self.create_code_response = self.client.post(
            reverse('user_registration:register'),
            data={
                "phone": self.phone_number,
            }
        )
        self.code = self.create_code_response.data["code"]

    def test_correct_response(self):
        response = self.client.post(
            reverse('user_registration:verify'),
            data={
                'code': self.code,
                'phone': self.phone_number,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Token.objects.count(), 1)

    def test_incorrect_code(self):
        response = self.client.post(
            reverse('user_registration:verify'),
            data={
                'code': '00a000',
                'phone': self.phone_number,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(Token.objects.count(), 0)
        self.assertEqual(response.data["error"], 'code is incorrect or expired')

    def test_expired_code(self):
        session = self.client.session

        data = session.get(self.phone_number)
        data['expire_time'] = '2000-10-10 10:10:10'
        session[self.phone_number] = data

        session.save()

        response = self.client.post(
            reverse('user_registration:verify'),
            data={
                'code': self.code,
                'phone': self.phone_number,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], 'code is incorrect or expired')
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(Token.objects.count(), 0)

    def test_empty_code(self):
        response = self.client.post(
            reverse('user_registration:verify'),
            data={
                'phone': self.phone_number,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], 'code is empty')
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(Token.objects.count(), 0)

    def test_dose_not_exist(self):
        response = self.client.post(
            reverse('user_registration:verify'),
            data={
                'code': '1234',
                'phone': '09123456789'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], 'code is incorrect or expired')
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(Token.objects.count(), 0)


class UserSetPasswordTest(test.APITestCase):

    def setUp(self):
        self.user_with_pass = User.objects.create_user(
            phone='09909998877',
            password='1234'
        )
        self.user_without_pass = User.objects.create(
            phone='09901112233'
        )
        self.user_without_pass.set_unusable_password()
        self.user_with_pass.save()

        self.factory = APIRequestFactory()

    def test_set_password_correct_by_user_without_pass(self):
        request = self.factory.post(
            reverse('user_registration:set_password'),
            data={
                'password': '1234',
                'password2': '1234'
            }
        )

        # set user
        force_authenticate(request, self.user_without_pass)

        response = UserSetPasswordView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user_without_pass.has_usable_password())

    def test_set_password_incorrect_by_user_without_pass(self):
        request = self.factory.post(
            reverse('user_registration:set_password'),
            data={
                'password': '1234',
                'password2': '123'
            }
        )

        # set user
        force_authenticate(request, self.user_without_pass)

        response = UserSetPasswordView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(self.user_without_pass.has_usable_password())

    def test_set_password_correct_by_user_with_password(self):
        request = self.factory.post(
            reverse('user_registration:set_password'),
            data={
                'old_password': '1234',
                'password': '4321',
                'password2': '4321'
            }
        )
        force_authenticate(request, self.user_with_pass)

        response = UserSetPasswordView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('password have been updated', response.data['message'])

    def test_incorrect_old_password(self):
        request = self.factory.post(
            reverse('user_registration:set_password'),
            data={
                'old_password': 'incorrect_pass',
                'password': 'new_pass',
                'password2': 'new_pass'
            }
        )
        force_authenticate(request, self.user_with_pass)

        response = UserSetPasswordView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('old_password is not correct', response.data['error'])

    def test_null_old_password(self):
        request = self.factory.post(
            reverse('user_registration:set_password'),
            data={
                'password': 'new_pass',
                'password2': 'new_pass'
            }
        )
        force_authenticate(request, self.user_with_pass)

        response = UserSetPasswordView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('old_password is not correct', response.data['error'])


class UserResetPasswordTest(test.APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            phone='09909998877',
            password='new_password'
        )
        self.client.force_authenticate(user=self.user)

        self.code_response = self.client.post(
            reverse('user_registration:register'),
            data={
                'phone': self.user.phone,
            }
        )
        self.code = self.code_response.data['code']

    def test_correct_code(self):
        response = self.client.post(
            reverse('user_registration:reset_password'),
            data={
                'code': self.code,
            }
        )
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(self.user.has_usable_password())

    def test_empty_code(self):
        response = self.client.post(
            reverse('user_registration:reset_password'),
        )
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(response.data.get('error'))
        self.assertIn('code is incorrect or expired', response.data.get('error'))


class UserChangeInfoTest(test.APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            phone='09909998877',
            first_name='amir',
            last_name='mirjamali',
            email='amir@gmail.com',
            bio="Hi I'm Amirhossein"
        )
        self.client.force_authenticate(self.user)

    def test_correct_info(self):
        response = self.client.patch(
            reverse('user_registration:change_info'),
            data={
                'first_name': 'ali',
                'last_name': 'amiri'
            }
        )
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.first_name, 'ali')
        self.assertEqual(self.user.last_name, 'amiri')


class UserDetailInfoTest(test.APITestCase):
    def setUp(self):
        self.user_1 = User.objects.create_user(
            phone='09909998877',
            first_name='ali',
            last_name='mirjamali',
            bio='Hi',
            email='amir@email.com'
        )
        self.user_2 = User.objects.create_user(
            phone='09909998866',
        )

    def test_correct_phone(self):
        self.client.force_authenticate(self.user_1)
        response = self.client.get(
            reverse('user_detail:detail', args=[self.user_1.phone]),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data.get('first_name'))
        self.assertEqual(response.data.get('first_name'), 'ali')
        self.assertEqual(response.data.get('email'), 'amir@email.com')

    def test_anonymous_user(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(
            reverse('user_detail:detail', args=[self.user_1.phone]),
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

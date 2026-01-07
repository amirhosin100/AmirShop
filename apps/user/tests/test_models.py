from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from apps.user.models import (
    User,
    Marketer,
    OTPManager,
    OTP
)


class UserModelFieldTest(TestCase):

    def test_false_is_staff(self):
        with self.assertRaisesMessage(ValueError, 'Superuser must have is_staff=True.'):
            User.objects.create_superuser(
                phone='09876543211',
                is_staff=False,
            )

    def test_false_is_superuser(self):
        with self.assertRaisesMessage(ValueError, 'Superuser must have is_superuser=True.'):
            User.objects.create_superuser(
                phone='09876543211',
                is_superuser=False,
            )

    def test_null_phone(self):
        with self.assertRaisesMessage(ValueError, 'Phone must not be null.'):
            User.objects.create_user(phone=None)

    def test_not_digit_phone(self):
        with self.assertRaisesMessage(ValueError, 'phone must be a number'):
            User.objects.create_user(phone='098765ab211')

    def test_short_length_phone(self):
        with self.assertRaisesMessage(ValueError, 'phone is not valid'):
            User.objects.create_user(phone='098765')

    def test_strat_phone_without_zero_and_nine(self):
        with self.assertRaisesMessage(ValueError, 'phone must start with <09>'):
            User.objects.create_user(phone='34567891109')


class UserModelTest(TestCase):

    def test_str_user(self):
        user = User.objects.create_user(
            phone='09876543211',
        )
        self.assertEqual(str(user), '09876543211')

    def test_get_full_name_without_first_name_and_last_name(self):
        user = User.objects.create_user(
            phone='09876543211',
        )
        self.assertEqual(user.get_full_name(), '')

    def test_get_full_name_with_first_name(self):
        user = User.objects.create_user(
            phone='09876543211',
            first_name='ali',
        )
        self.assertEqual(user.get_full_name(), 'ali')

    def test_get_full_name_with_last_name(self):
        user = User.objects.create_user(
            phone='09876543211',
            last_name='mirjamali',
        )
        self.assertEqual(user.get_full_name(), 'mirjamali')

    def test_get_full_name_with_first_name_and_last_name(self):
        user = User.objects.create_user(
            phone='09876543211',
            first_name='amirhossein',
            last_name='mirjamali',
        )
        self.assertEqual(user.get_full_name(), 'amirhossein mirjamali')


class MarketerModelTest(TestCase):

    def test_str_marketer(self):
        user = User.objects.create_user(
            phone='09876543211'
        )
        marketer = Marketer.objects.create(
            user=user,
            age=20,
            national_code="1234567890",
            city="city",
            province="province",
            address="address",
        )
        self.assertEqual(str(marketer), '09876543211')
        self.assertEqual(Marketer.objects.count(), 1)


class OTPManagerTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.phone = '09123456789'

    def setUp(self):
        self.otp = OTP.codes.create_code(phone=self.phone)
        self.code = self.otp.code

    def test_create_code_method(self):
        self.assertEqual(OTP.objects.count(), 1)

        # create again
        with self.assertRaisesMessage(ValueError, 'Code already exists.'):
            OTP.codes.create_code(phone=self.phone)

        self.assertEqual(OTP.objects.count(), 1)

        # make expire
        otp = OTP.objects.get(phone=self.phone)
        otp.created_at = timezone.now() - timedelta(days=1)
        otp.save()
        OTP.codes.create_code(phone=self.phone)
        self.assertEqual(OTP.objects.count(), 1)

    def test_by_incorrect_phone(self):
        # test by incorrect phone
        with self.assertRaisesMessage(ValueError, 'Phone Number or Code does not exist.'):
            OTP.codes.check_code(phone="09137776655", code=self.code)
        self.assertEqual(OTP.objects.count(), 1)

    def test_by_not_active(self):
        # test by not active
        self.otp.created_at = timezone.now() - timedelta(days=1)
        self.otp.save()
        with self.assertRaisesMessage(ValueError, 'Code is expired.'):
            OTP.codes.check_code(phone=self.phone, code=self.code)
        self.assertEqual(OTP.objects.count(), 1)

    def test_by_incorrect_code(self):
        # test by incorrect code
        with self.assertRaisesMessage(ValueError, 'Code does not match.'):
            OTP.codes.check_code(phone=self.phone, code='1234a')
        self.assertEqual(OTP.objects.count(), 1)

    def test_correct_code(self):
        check = OTP.codes.check_code(phone=self.phone, code=self.code)
        self.assertTrue(check)
        self.assertEqual(OTP.objects.count(), 0)

    def test_time_to_be_expired_by_incorrect_phone(self):
        with self.assertRaisesMessage(ValueError, 'Phone Number or Code does not exist.'):
            OTP.codes.time_to_be_expired(phone='09123456700')

    def test_time_to_be_expired_by_not_active(self):
        self.otp.created_at = timezone.now() - timedelta(days=1)
        self.otp.save()
        self.assertFalse(OTP.codes.time_to_be_expired(phone=self.phone))

    def test_correct_time_to_be_expired_method(self):
        self.assertIsNotNone(OTP.codes.time_to_be_expired(phone=self.phone))


class OTPModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.phone = '09123456789'
        cls.otp = OTP.objects.create(phone=cls.phone)

    def setUp(self):
        self.assertIsNotNone(self.otp.code)

    def test_is_active_expire(self):
        self.otp.created_at = timezone.now() - timedelta(days=1)
        self.otp.save()
        self.assertFalse(self.otp.is_active)

    def test_is_active_not_expire(self):
        self.otp.created_at = timezone.now()
        self.otp.save()
        self.assertTrue(self.otp.is_active)

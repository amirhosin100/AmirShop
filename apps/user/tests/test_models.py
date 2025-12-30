from django.test import TestCase
from apps.user.models import User,Marketer


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
        )
        self.assertEqual(str(marketer), '09876543211')
        self.assertEqual(Marketer.objects.count(), 1)
        self.assertEqual(Marketer.objects.count(), 1)
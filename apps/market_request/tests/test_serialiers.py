from rest_framework import test
from rest_framework.exceptions import ValidationError
from apps.market_request.serializer import (
    MarketRequestSerializer
)
from apps.user.models import User
from apps.market_request.models import MarketRequest


class MarketRequestSerializerTest(test.APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            phone="09123456789",
        )

    def setUp(self):
        self.data = {
            "mobile_number" : "09123456789",
            "city" : "city",
            "province" : "province",
            "address" : f"{'address'*5}",
            "description" : f"{'description_'*10}",
            "national_code" : "1234567890",
            "age": 30,
        }

    def test_read_only_fields(self):
        self.assertCountEqual(
            ('id', 'created_at', 'updated_at'),
            MarketRequestSerializer.Meta.read_only_fields
        )

    def test_has_user_in_fields(self):
        self.assertNotIn('user', MarketRequestSerializer.Meta.fields)

    def test_phone_not_digit(self):
        self.data['mobile_number'] = "0913abc2244"
        serializer = MarketRequestSerializer(data=self.data)
        with self.assertRaisesMessage(ValidationError,"phone must be a number"):
            serializer.is_valid(raise_exception=True)
        self.assertEqual(MarketRequest.objects.count(), 0)

    def test_phone_not_equal_length(self):
        self.data['mobile_number'] = "0913"
        serializer = MarketRequestSerializer(data=self.data)
        with self.assertRaisesMessage(ValidationError,"phone is not valid"):
            serializer.is_valid(raise_exception=True)
        self.assertEqual(MarketRequest.objects.count(), 0)

    def test_phone_strat_without_zero_nine(self):
        self.data['mobile_number'] = "12345678900"
        serializer = MarketRequestSerializer(data=self.data)
        with self.assertRaisesMessage(ValidationError,"phone must start with <09>"):
            serializer.is_valid(raise_exception=True)
        self.assertEqual(MarketRequest.objects.count(), 0)

    def test_correct_phone(self):
        self.data['mobile_number'] = "09135558811"
        serializer = MarketRequestSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(MarketRequest.objects.count(), 0)

    def test_length_city(self):
        self.data['city'] = "a"
        serializer = MarketRequestSerializer(data=self.data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)
        self.assertEqual(MarketRequest.objects.count(), 0)

    def test_validate_description(self):
        self.data['description'] = "1"*99
        serializer = MarketRequestSerializer(data=self.data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)
        self.assertEqual(MarketRequest.objects.count(), 0)

    def test_validate_address(self):
        self.data['address'] = "1"*29
        serializer = MarketRequestSerializer(data=self.data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)
        self.assertEqual(MarketRequest.objects.count(), 0)

    def test_correct_data(self):
        serializer = MarketRequestSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertEqual(MarketRequest.objects.count(), 1)

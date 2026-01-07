from rest_framework import test, serializers
from apps.market.serializer.market_serializer import (
    MarketOwnerSerializer,
    MarketUserSerializer
)


class MarketOwnerSerializerTest(test.APITestCase):

    def test_has_correct_fields(self):
        self.assertCountEqual(
            ['created_at', 'updated_at','id','is_active'],
            MarketOwnerSerializer.Meta.read_only_fields
        )
        self.assertCountEqual(
            ['marketer'],
            MarketOwnerSerializer.Meta.exclude
        )

    def test_invalid_market_name(self):
        serializer = MarketOwnerSerializer(
            data={'market_name':'t'}
        )
        with self.assertRaises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_valid_market_name(self):
        serializer = MarketOwnerSerializer(
            data={'market_name':'amir'}
        )
        self.assertEqual(serializer.validate_name(serializer.initial_data['market_name']),'amir')


class MarketUserSerializerTest(test.APITestCase):

    def test_has_correct_fields(self):
        self.assertCountEqual(
            ['id','created_at'],
            MarketUserSerializer.Meta.read_only_fields
        )
        self.assertCountEqual(
            ['is_active','updated_at'],
            MarketUserSerializer.Meta.exclude
        )
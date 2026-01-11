import os
import shutil
import uuid
from io import BytesIO

from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.exceptions import ValidationError
from PIL import Image

from apps.user.models import User, Marketer
from apps.market.models import Market
from apps.product.models import Product, ProductImage, ProductFeature
from apps.product.serializer.common_seializer import (
    ProductImageSerializer,
    ProductFeatureSerializer,
    ProductDetailSerializer,
)
from apps.product.serializer.owner_serializer import (
    ProductOwnerCreateSerializer,
    ProductOwnerUpdateSerializer,
)
from apps.product.serializer.user_serializer import ProductSimpleSerializer

TEST_MEDIA_ROOT = os.path.join(os.path.dirname(__file__), "test_media")


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class ProductSerializerTests(TestCase):

    def setUp(self):
        # user / marketer / market
        self.user = User.objects.create_user(phone="09909998877", password="123456")
        self.marketer = Marketer.objects.create(
            user=self.user,
            age=20,
            national_code="1234567890",
            city="city",
            province="province",
            address="address",
        )
        self.market = Market.objects.create(
            marketer=self.marketer,
            name="Test Market"
        )

        self.product = Product.objects.create(
            market=self.market,
            name="Test Product",
            price=1000,
            percentage_off=10,
            stock=5,
            description="desc"
        )

    def tearDown(self):
        if os.path.exists(TEST_MEDIA_ROOT):
            shutil.rmtree(TEST_MEDIA_ROOT)

    # ---------------- helpers ----------------
    def generate_image(self, name="test.jpg"):
        img = BytesIO()
        Image.new("RGB", (100, 100)).save(img, "JPEG")
        img.seek(0)
        return SimpleUploadedFile(name, img.read(), content_type="image/jpeg")

    # ================= ProductImageSerializer =================
    def test_product_image_serializer(self):
        image = ProductImage.objects.create(
            product=self.product,
            title="Cover",
            image=self.generate_image()
        )

        serializer = ProductImageSerializer(image)
        data = serializer.data

        self.assertEqual(data["title"], "Cover")
        self.assertIn("url", data)
        self.assertTrue(data["url"].endswith("test.jpg"))

    # ================= ProductFeatureSerializer =================
    def test_product_feature_serializer(self):
        feature = ProductFeature.objects.create(
            product=self.product,
            key="Color",
            value="Red"
        )

        serializer = ProductFeatureSerializer(feature)
        data = serializer.data

        self.assertEqual(data["key"], "Color")
        self.assertEqual(data["value"], "Red")

    # ================= ProductDetailSerializer =================
    def test_product_detail_serializer_with_images_and_features(self):
        ProductImage.objects.create(
            product=self.product,
            title="Img",
            image=self.generate_image()
        )
        ProductFeature.objects.create(
            product=self.product,
            key="Size",
            value="XL"
        )

        serializer = ProductDetailSerializer(self.product)
        data = serializer.data

        self.assertEqual(data["name"], self.product.name)
        self.assertEqual(len(data["images"]), 1)
        self.assertEqual(len(data["features"]), 1)
        self.assertEqual(data["features"][0]["key"], "Size")

    # ================= ProductSimpleSerializer =================
    def test_product_simple_serializer_first_image(self):
        img1 = ProductImage.objects.create(
            product=self.product,
            title="First",
            image=self.generate_image("1.jpg")
        )
        ProductImage.objects.create(
            product=self.product,
            title="Second",
            image=self.generate_image("2.jpg")
        )

        serializer = ProductSimpleSerializer(self.product)
        data = serializer.data

        self.assertEqual(data["image"]["title"], img1.title)

    def test_product_simple_serializer_no_image(self):
        serializer = ProductSimpleSerializer(self.product)
        data = serializer.data

        self.assertIsNone(data["image"])

    # ================= ProductOwnerCreateSerializer =================
    def test_owner_create_serializer_valid(self):
        payload = {
            "name": "New Product",
            "description": "desc",
            "price": 200,
            "percentage_off": 10,
            "discount_price": 180,
            "stock": 10,
            "images": [
                {
                    "title": "img",
                    "image": self.generate_image()
                }
            ],
            "features": [
                {
                    "key": "Color",
                    "value": "Blue"
                }
            ]
        }

        serializer = ProductOwnerCreateSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        product = serializer.create(
            serializer.validated_data,
            market_id=self.market.id
        )

        self.assertEqual(product.name, "New Product")
        self.assertEqual(product.images.count(), 1)
        self.assertEqual(product.features.count(), 1)

    def test_owner_create_serializer_invalid_name(self):
        serializer = ProductOwnerCreateSerializer(
            data={
                "name": "A",
                "price": 100,
                "percentage_off": 0,
                "discount_price": 100,
                "stock": 1
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)

    def test_owner_create_serializer_invalid_price(self):
        serializer = ProductOwnerCreateSerializer(
            data={
                "name": "Valid Name",
                "price": 0,
                "percentage_off": 0,
                "discount_price": 0,
                "stock": 1
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("price", serializer.errors)

    # ================= ProductOwnerUpdateSerializer =================
    def test_owner_update_serializer_valid(self):
        serializer = ProductOwnerUpdateSerializer(
            instance=self.product,
            data={
                "name": "Updated",
                "price": 300,
                "percentage_off": 0,
                "discount_price": 300,
                "stock": 2
            },
            partial=True
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        product = serializer.save()

        self.assertEqual(product.name, "Updated")
        self.assertEqual(product.price, 300)

    def test_owner_update_serializer_invalid_name(self):
        serializer = ProductOwnerUpdateSerializer(
            instance=self.product,
            data={"name": "A"},
            partial=True
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)

    def test_owner_create_serializer_read_only_fields_ignored(self):
        test_id = uuid.uuid4()
        payload = {
            "id": test_id,
            "market": 999,
            "name": "Readonly Test",
            "description": "desc",
            "price": 100,
            "percentage_off": 0,
            "discount_price": 100,
            "stock": 1,
        }

        serializer = ProductOwnerCreateSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        product = serializer.create(
            serializer.validated_data,
            market_id=self.market.id
        )

        # id از payload نباید ست شده باشد
        self.assertNotEqual(product.id, test_id)

        # market باید همان market پاس داده شده به create باشد
        self.assertEqual(product.market, self.market)

    def test_owner_create_serializer_market_cannot_be_set_from_payload(self):
        another_market = Market.objects.create(
            marketer=self.marketer,
            name="Another Market"
        )

        payload = {
            "market": another_market.id,
            "name": "Market Test",
            "price": 200,
            "percentage_off": 0,
            "discount_price": 200,
            "stock": 5,
        }

        serializer = ProductOwnerCreateSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        product = serializer.create(
            serializer.validated_data,
            market_id=self.market.id
        )

        # market نباید از payload گرفته شود
        self.assertEqual(product.market, self.market)

    def test_owner_update_serializer_read_only_id(self):
        old_id = self.product.id

        serializer = ProductOwnerUpdateSerializer(
            instance=self.product,
            data={
                "id": 999,
                "name": "Updated Name"
            },
            partial=True
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        product = serializer.save()

        self.assertEqual(product.id, old_id)

    def test_owner_update_serializer_does_not_allow_unexpected_fields(self):
        serializer = ProductOwnerUpdateSerializer(
            instance=self.product,
            data={
                "id": 999,
                "stock": 99
            },
            partial=True
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        product = serializer.save()

        self.assertEqual(product.stock, 99)
        self.assertNotEqual(product.id, 999)

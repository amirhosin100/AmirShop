import os
import shutil
from django.urls import reverse
from django.test import override_settings
from rest_framework.test import APITestCase
from rest_framework import status
from apps.user.models import User, Marketer
from apps.market.models import Market
from apps.product.models import Product, ProductImage, ProductFeature
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from PIL import Image
from uuid import uuid4

TEST_MEDIA_ROOT = os.path.join(os.path.dirname(__file__), 'test_media')


#@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class ProductViewPermissionTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        # ایجاد کاربر
        cls.user = User.objects.create_user(phone="09909998877", password="password123")
        Marketer.objects.create(
            user=cls.user,
            age=20,
            national_code="1234567890",
            city="city",
            province="province",
            address="address",
        )

        # ایجاد مارکت
        cls.market = Market.objects.create(marketer=cls.user.marketer, name="TestMarket")

    def setUp(self):

        # ایجاد محصول
        self.product = Product.objects.create(
            market=self.market,
            name="Test Product",
            price=1000,
            percentage_off=10,
            stock=50
        )

        # ایجاد تصویر برای محصول
        img = BytesIO()
        image = Image.new('RGB', (100, 100))
        image.save(img, 'JPEG')
        img.seek(0)
        self.product_image = ProductImage.objects.create(
            product=self.product,
            title="Test Image",
            image=SimpleUploadedFile("test.jpg", img.read(), content_type="image/jpeg")
        )

        # ایجاد ویژگی محصول
        self.feature = ProductFeature.objects.create(
            product=self.product,
            key="Color",
            value="Red"
        )

        self.list_url = reverse('product_user:product_list')
        self.detail_url = reverse('product_user:product_detail', args=[self.product.id])
        self.invalid_detail_url = reverse('product_user:product_detail', args=[uuid4()])

    def tearDown(self):
        # حذف فایل‌های تصویر و پوشه تست
        if os.path.exists(TEST_MEDIA_ROOT):
            shutil.rmtree(TEST_MEDIA_ROOT)

    # ---------------- List View ----------------
    def test_product_list_anonymous_denied(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_product_list_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], self.product.name)
        self.assertIn('image', response.data[0])

    def test_product_list_filter(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url, {'q': 'Test'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        response = self.client.get(self.list_url, {'q': 'NonExisting'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    # ---------------- Detail View ----------------
    def test_product_detail_anonymous_denied(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_product_detail_authenticated_exists(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.product.id))
        self.assertIn('images', response.data)
        self.assertIn('features', response.data)
        self.assertEqual(len(response.data['images']), 1)
        self.assertEqual(len(response.data['features']), 1)

    def test_product_detail_authenticated_not_exists(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.invalid_detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('message', response.data)

    # ---------------- Discount Price ----------------
    def test_product_discount_price_calculation(self):
        self.assertEqual(self.product.discount_price, 900)  # 10% off 1000

    def test_product_discount_price_zero_percentage(self):
        product = Product.objects.create(
            market=self.market,
            name="No Discount Product",
            price=500,
            percentage_off=0
        )
        self.assertEqual(product.discount_price, 500)

    def test_product_with_multiple_images(self):
        # اضافه کردن تصویر دوم
        img = BytesIO()
        Image.new('RGB', (50, 50)).save(img, 'JPEG')
        img.seek(0)
        ProductImage.objects.create(
            product=self.product,
            title="Second Image",
            image=SimpleUploadedFile("second.jpg", img.read(), content_type="image/jpeg")
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['images']), 2)

    def test_product_without_image_or_feature(self):
        product = Product.objects.create(
            market=self.market,
            name="Empty Product",
            price=100
        )
        self.client.force_authenticate(user=self.user)
        detail_url = reverse('product_user:product_detail', args=[product.id])
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['images']), 0)
        self.assertEqual(len(response.data['features']), 0)

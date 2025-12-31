import os
import shutil
from django.test import TestCase, override_settings
from apps.market.models import Market
from apps.user.models import User, Marketer
from apps.product.models import Product, ProductImage, ProductFeature
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from PIL import Image


TEST_MEDIA_ROOT = os.path.join(os.path.dirname(__file__), 'test_media')


# ===================== PRODUCT MODEL TESTS =====================
@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class ProductModelTests(TestCase):

    def setUp(self):
        # ایجاد کاربر و مارکت
        self.user = User.objects.create_user(phone="09909998877", password="password123")
        Marketer.objects.create(user=self.user)
        self.market = Market.objects.create(marketer=self.user.marketer, name="TestMarket")

        # ایجاد محصول نمونه
        self.product = Product.objects.create(
            market=self.market,
            name="Test Product",
            price=1000,
            percentage_off=10,
            stock=50
        )

    def tearDown(self):
        # حذف فایل‌های تصویر و پوشه تست
        if os.path.exists(TEST_MEDIA_ROOT):
            shutil.rmtree(TEST_MEDIA_ROOT)

    # ===================== HELPER FUNCTION =====================
    def create_image(self, product, title="Test Image"):
        img = BytesIO()
        image = Image.new('RGB', (100, 100))
        image.save(img, 'JPEG')
        img.seek(0)
        return ProductImage.objects.create(
            product=product,
            title=title,
            image=SimpleUploadedFile(f"{title}.jpg", img.read(), content_type="image/jpeg")
        )

    # ===================== PRODUCT TESTS =====================
    def test_product_creation(self):
        self.assertEqual(self.product.name, "Test Product")
        self.assertEqual(self.product.price, 1000)
        self.assertEqual(self.product.percentage_off, 10)
        self.assertEqual(self.product.discount_price, 900)  # 10% off
        self.assertEqual(self.product.stock, 50)
        self.assertEqual(str(self.product), self.product.name)

    def test_product_discount_zero(self):
        product = Product.objects.create(
            market=self.market,
            name="No Discount",
            price=500,
            percentage_off=0
        )
        self.assertEqual(product.discount_price, 500)

    def test_product_discount_100_percent(self):
        product = Product.objects.create(
            market=self.market,
            name="Free Product",
            price=200,
            percentage_off=100
        )
        self.assertEqual(product.discount_price, 0)

    # ===================== PRODUCT IMAGE TESTS =====================
    def test_product_image_creation(self):
        img = self.create_image(self.product)
        self.assertEqual(img.product, self.product)
        self.assertEqual(img.title, "Test Image")
        self.assertTrue(os.path.exists(img.image.path))
        self.assertEqual(str(img), "Test Image")

    def test_product_multiple_images(self):
        img1 = self.create_image(self.product, title="Image1")
        img2 = self.create_image(self.product, title="Image2")
        self.assertEqual(self.product.images.count(), 2)

    # ===================== PRODUCT FEATURE TESTS =====================
    def test_product_feature_creation(self):
        feature = ProductFeature.objects.create(product=self.product, key="Color", value="Red")
        self.assertEqual(feature.product, self.product)
        self.assertEqual(feature.key, "Color")
        self.assertEqual(feature.value, "Red")
        self.assertEqual(str(feature), "Color : Red")

    def test_product_feature_unique_constraint(self):
        ProductFeature.objects.create(product=self.product, key="Size", value="L")
        with self.assertRaises(Exception):
            # ایجاد دوباره با همان key باید خطا بدهد
            ProductFeature.objects.create(product=self.product, key="Size", value="M")

    def test_product_feature_multiple_keys(self):
        ProductFeature.objects.create(product=self.product, key="Size", value="L")
        ProductFeature.objects.create(product=self.product, key="Material", value="Cotton")
        self.assertEqual(self.product.features.count(), 2)

    # ===================== PRODUCT ORDERING =====================
    def test_product_ordering_by_name(self):
        Product.objects.create(market=self.market, name="A Product", price=100)
        Product.objects.create(market=self.market, name="Z Product", price=200)
        names = list(Product.objects.all().values_list('name', flat=True))
        self.assertCountEqual(names, sorted(names))  # Ordered by name as defined in Meta

    # ===================== PRODUCT IMAGE PATH =====================
    def test_product_image_path(self):
        img = self.create_image(self.product, title="PathTest")
        expected_path = f"{self.product.market.name}/{self.product.name}/PathTest.jpg"
        self.assertIn(expected_path, img.image.name)

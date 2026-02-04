from rest_framework.test import APITestCase,override_settings
import shutil
from rest_framework import status
from django.urls import reverse
from apps.user.models import User, Marketer
from apps.market.models import Market
from apps.product.models import Product, ProductImage, ProductFeature
from apps.category.models import SubCategory
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from io import BytesIO
import os

TEST_MEDIA_ROOT = os.path.join(os.path.dirname(__file__), 'test_media')


# ===================== HELPER FUNCTION =====================
def get_test_image_file(name="test.jpg"):
    """
    Create a dummy JPEG image file for testing purposes.
    """
    file_obj = BytesIO()
    image = Image.new("RGB", (100, 100), color="white")
    image.save(file_obj, format="JPEG")
    file_obj.seek(0)
    return SimpleUploadedFile(name, file_obj.read(), content_type="image/jpeg")


# ===================== BASE TEST SETUP =====================
@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class BaseTestSetup(APITestCase):

    @classmethod
    def setUpTestData(cls):
        # Users
        cls.user = User.objects.create_user(phone="09901234567", password="pass")
        cls.other_user = User.objects.create_user(phone="09907654321", password="pass")
        cls.category = SubCategory.objects.first()
        # Marketer and Market
        cls.marketer = Marketer.objects.create(
            user=cls.user,
            age=20,
            national_code="1234567890",
            city="city",
            province="province",
            address="address",
        )
        cls.market = Market.objects.create(name="Test Market", marketer=cls.marketer)

    def setUp(self):
        # Product
        self.product = Product.objects.create(
            category=self.category,
            market=self.market,
            name="Test Product",
            description="desc",
            price=100,
            percentage_off=0,
            discount_price=100,
            stock=10
        )

        # Initial product image
        self.image = ProductImage.objects.create(
            product=self.product,
            title="Initial Image",
            image=get_test_image_file("initial.jpg")
        )

        # Product feature
        self.feature = ProductFeature.objects.create(product=self.product, key="color", value="red")

    def tearDown(self):
        # حذف فایل‌های تصویر و پوشه تست
        if os.path.exists(TEST_MEDIA_ROOT):
            shutil.rmtree(TEST_MEDIA_ROOT)


# ===================== PRODUCT TESTS =====================
class ProductViewTests(BaseTestSetup):

    def test_create_product_success(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('product_owner:product_create', kwargs={'market_id': self.market.id})
        data = {
            "name": "New Product",
            "description": "desc",
            "price": 50,
            "percentage_off": 0,
            "discount_price": 50,
            "stock": 5,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], "New Product")

    def test_create_product_permission_denied(self):
        self.client.force_authenticate(user=self.other_user)
        url = reverse('product_owner:product_create', kwargs={'market_id': self.market.id})
        data = {
            "name": "New Product",
            "description": "desc",
            "price": 50,
            "percentage_off": 0,
            "discount_price": 50,
            "stock": 5
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_product_success(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('product_owner:product_update', kwargs={'product_id': self.product.id})
        data = {"name": "Updated Product"}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Updated Product")

    def test_update_product_permission_denied(self):
        self.client.force_authenticate(user=self.other_user)
        url = reverse('product_owner:product_update', kwargs={'product_id': self.product.id})
        data = {"name": "Updated Product"}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_product_success(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('product_owner:product_delete', kwargs={'product_id': self.product.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Product.objects.filter(id=self.product.id).exists())

    def test_delete_product_permission_denied(self):
        self.client.force_authenticate(user=self.other_user)
        url = reverse('product_owner:product_delete', kwargs={'product_id': self.product.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_product_detail_success(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('product_owner:product_detail', kwargs={'product_id': self.product.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.product.id))

    def test_product_detail_permission_denied(self):
        self.client.force_authenticate(user=self.other_user)
        url = reverse('product_owner:product_detail', kwargs={'product_id': self.product.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_product_list_success(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('product_owner:product_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_product_list_permission_denied(self):
        self.client.force_authenticate(user=self.other_user)
        url = reverse('product_owner:product_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


# ===================== PRODUCT FEATURE TESTS =====================
class ProductFeatureViewTests(BaseTestSetup):

    def test_feature_create_success(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('product_owner:feature_create', kwargs={'product_id': self.product.id})
        data = {"key": "size", "value": "large"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_feature_create_permission_denied(self):
        self.client.force_authenticate(user=self.other_user)
        url = reverse('product_owner:feature_create', kwargs={'product_id': self.product.id})
        data = {"key": "size", "value": "large"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_feature_create_anonymous(self):
        url = reverse('product_owner:feature_create', kwargs={'product_id': self.product.id})
        data = {"key": "size", "value": "large"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_feature_update_permission_denied(self):
        self.client.force_authenticate(user=self.other_user)
        url = reverse(
            'product_owner:feature_update',
            kwargs={'product_id': self.product.id, 'feature_id': self.feature.id}
        )
        data = {"value": "blue"}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_feature_update_anonymous(self):
        url = reverse(
            'product_owner:feature_update',
            kwargs={'product_id': self.product.id, 'feature_id': self.feature.id}
        )
        data = {"value": "blue"}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_feature_delete_permission_denied(self):
        self.client.force_authenticate(user=self.other_user)
        url = reverse(
            'product_owner:feature_delete',
            kwargs={'product_id': self.product.id, 'feature_id': self.feature.id}
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_feature_delete_anonymous(self):
        url = reverse(
            'product_owner:feature_delete',
            kwargs={'product_id': self.product.id, 'feature_id': self.feature.id}
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# ===================== PRODUCT IMAGE TESTS =====================
class ProductImageViewTests(BaseTestSetup):

    # ======= CREATE =======
    def test_image_create_success(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('product_owner:image_create', kwargs={'product_id': self.product.id})
        image_file = get_test_image_file("new_image.jpg")
        data = {"title": "New Image", "image": image_file}
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], "New Image")

    def test_image_create_permission_denied(self):
        self.client.force_authenticate(user=self.other_user)
        url = reverse('product_owner:image_create', kwargs={'product_id': self.product.id})
        image_file = get_test_image_file("new_image.jpg")
        data = {"title": "New Image", "image": image_file}
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_image_create_anonymous(self):
        url = reverse('product_owner:image_create', kwargs={'product_id': self.product.id})
        image_file = get_test_image_file("anon_image.jpg")
        data = {"title": "New Image", "image": image_file}
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ======= UPDATE =======
    def test_image_update_success(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('product_owner:image_update', kwargs={'product_id': self.product.id, 'image_id': self.image.id})
        data = {"title": "Updated Image"}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Updated Image")

    def test_image_update_permission_denied(self):
        self.client.force_authenticate(user=self.other_user)
        url = reverse('product_owner:image_update', kwargs={'product_id': self.product.id, 'image_id': self.image.id})
        data = {"title": "Updated Image"}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_image_update_anonymous(self):
        url = reverse('product_owner:image_update', kwargs={'product_id': self.product.id, 'image_id': self.image.id})
        data = {"title": "Updated Image"}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ======= DELETE =======
    def test_image_delete_success(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('product_owner:image_delete', kwargs={'product_id': self.product.id, 'image_id': self.image.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(ProductImage.objects.filter(id=self.image.id).exists())

    def test_image_delete_permission_denied(self):
        self.client.force_authenticate(user=self.other_user)
        url = reverse('product_owner:image_delete', kwargs={'product_id': self.product.id, 'image_id': self.image.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_image_delete_anonymous(self):
        url = reverse('product_owner:image_delete', kwargs={'product_id': self.product.id, 'image_id': self.image.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

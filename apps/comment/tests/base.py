from rest_framework.test import APITestCase, APIClient, override_settings
from django.urls import reverse
import os
from utils.image import create_image, clear_images
from apps.product.models import Product
from apps.user.models import User, Marketer
from apps.market.models import Market
from apps.comment.models import Comment, CommentImage

TEST_MEDIA_ROOT = os.path.join(os.path.dirname(__file__), 'test_media')


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class BaseTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            phone='09123456789',
            first_name='amir',
        )

        cls.other_user = User.objects.create_user(
            phone='09123456799'
        )

        Marketer.objects.create(
            user=cls.user,
            national_code='foo',
            age=20,
            city='foo',
            province='foo',
            address='foo',
        )

        cls.market = Market.objects.create(
            marketer=cls.user.marketer,
            name='test_market',
        )

        cls.product = Product.objects.create(
            market=cls.market,
            name='test_product',
            price=1000,
        )

        cls.comment = Comment.objects.create(
            user=cls.user,
            product=cls.product,
            content='test_comment',
            score=4
        )

        cls.image = create_image()

        cls.image_comment_1 = CommentImage.objects.create(
            comment=cls.comment,
            image=cls.image,
        )

        cls.data = {
            "content": "test_content",
            "score": 3
        }
        cls.image_data = {
            "image": cls.image,
        }
        cls.create_comment_url = lambda product_id: reverse('comment_user:create', args=[product_id])
        cls.create_comment_image_url = lambda comment_id: reverse('comment_user:image_create', args=[comment_id])
        cls.list_owner_url = reverse('comment_owner:list')
        cls.detail_comment_url = lambda comment_id: reverse('comment_owner:detail', args=[comment_id])

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        clear_images(TEST_MEDIA_ROOT)

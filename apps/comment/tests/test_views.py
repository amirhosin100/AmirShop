from rest_framework import status
from uuid import uuid4
from utils.image import create_image
from apps.comment.models import Comment, CommentImage
from .base import BaseTestCase


class CommentCreateViewTest(BaseTestCase):
    def test_comment_create_view_by_anonymous_user(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(
            self.create_comment_url(self.product.id),
            data=self.data,
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Comment.objects.count(), 1)

    def test_comment_create_view_by_authenticated_user(self):
        response = self.client.post(
            self.create_comment_url(self.product.id),
            data=self.data,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 2)

    def test_comment_create_view_by_incorrect_product_id(self):
        response = self.client.post(
            self.create_comment_url(uuid4()),
            data=self.data,
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('does not exist', response.data['error'])
        self.assertEqual(Comment.objects.count(), 1)

    def test_comment_create_view_by_incorrect_data(self):
        response = self.client.post(
            self.create_comment_url(self.product.id),
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Comment.objects.count(), 1)


class CommentImageCreateViewTest(BaseTestCase):
    def test_comment_image_create_view_by_anonymous_user(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(
            self.create_comment_image_url(self.comment.id),
            data=self.image_data,
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(CommentImage.objects.count(), 1)

    def test_comment_image_create_view_by_owner_user(self):
        response = self.client.post(
            self.create_comment_image_url(self.comment.id),
            data={
                "image": create_image('m')
            },
            format='multipart'

        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('m.jpg', response.data['image'])
        self.assertEqual(CommentImage.objects.count(), 2)

    def test_comment_image_create_view_by_other_user(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.post(
            self.create_comment_image_url(self.comment.id),
            data={"image": create_image('test_img')},
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(CommentImage.objects.count(), 1)

    def test_comment_image_create_view_by_incorrect_comment_id(self):
        response = self.client.post(
            self.create_comment_image_url(uuid4()),
            data={"image": create_image('test_img')},
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(CommentImage.objects.count(), 1)


class CommentListOwnerViewTest(BaseTestCase):
    def test_comment_list_view_by_anonymous_user(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.list_owner_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_comment_list_view_by_authenticate_user(self):
        response = self.client.get(self.list_owner_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data),1)

    def test_comment_list_view_by_other_user(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self.list_owner_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data),0)


class CommentDetailOwnerViewTest(BaseTestCase):
    def test_comment_detail_view_by_anonymous_user(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(
            self.detail_comment_url(self.comment.id),
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_comment_detail_view_by_authenticate_user(self):
        response = self.client.get(self.detail_comment_url(self.comment.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user_name'],'amir')
        self.assertEqual(response.data['product_name'],'test_product')
        self.assertEqual(response.data['product'],self.product.id)

    def test_comment_detail_view_by_other_user(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self.detail_comment_url(self.comment.id))

        self.assertEqual(response.status_code,status.HTTP_404_NOT_FOUND)

    def test_comment_detail_view_by_incorrect_comment_id(self):
        response = self.client.get(self.detail_comment_url(uuid4()))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


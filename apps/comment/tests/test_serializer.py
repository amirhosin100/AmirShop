from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase

from apps.comment.serializers.user_serializer import (
    CommentSerializer,
    CommentImageSerializer
)
from apps.comment.serializers.owner_serializer import (
    CommentDetailSerializer,
    CommentImageDetailSerializer
)
from apps.comment.models import Comment


class CommentSerializerTest(APITestCase):

    def setUp(self):
        self.data = {
            'content': 'test comment',
            'score': 5,
        }

    def test_read_only_fields(self):
        self.assertCountEqual(
            CommentSerializer.Meta.read_only_fields,
            ['id', 'updated_at', 'created_at']
        )

    def test_correct_serializer(self):
        serializer = CommentSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())

    def test_gt_score(self):
        self.data['score'] = 10
        serializer = CommentSerializer(data=self.data)
        with self.assertRaisesMessage(ValidationError, 'score must be between 1 and 5'):
            serializer.is_valid(raise_exception=True)

    def test_lt_score(self):
        self.data['score'] = 0
        serializer = CommentSerializer(data=self.data)
        with self.assertRaisesMessage(ValidationError, 'score must be between 1 and 5'):
            serializer.is_valid(raise_exception=True)


class CommentImageSerializerTest(APITestCase):

    def test_read_only_fields(self):
        self.assertCountEqual(
            CommentImageSerializer.Meta.read_only_fields,
            ['id']
        )


class CommentImageDetailSerializerTest(APITestCase):

    def test_read_only_fields(self):
        self.assertCountEqual(
            CommentImageDetailSerializer.Meta.read_only_fields,
            ['id','image']
        )

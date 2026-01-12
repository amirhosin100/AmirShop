from .base import BaseTestCase
from apps.comment.models import Comment

class CommentModelTest(BaseTestCase):

    def setUp(self):
        self.assertIsNone(self.product.score)
        self.comment.status = Comment.CommentStatus.PUBLISHED
        self.comment.save()
        # 4.0, 4.0
        self.assertEqual(self.product.score, self.comment.score)

        self.new_comment = Comment.objects.create(
            user=self.user,
            product=self.product,
            content="test comment",
            score=1,
            status=Comment.CommentStatus.PUBLISHED,
        )
        self.product.refresh_from_db()
        # 4.0 + 1.0 = 5 => 5 / 2 = 2.5
        self.assertEqual(self.product.score, 2.5)

    def test_changed_status_to_draft_comment(self):
        self.new_comment.status = Comment.CommentStatus.DRAFT
        self.new_comment.save()
        self.product.refresh_from_db()
        self.assertEqual(self.product.score,4)

    def test_changed_status_to_rejected_comment(self):
        self.comment.status = Comment.CommentStatus.REJECTED
        self.comment.save()
        self.assertEqual(self.product.score,1)

    def test_deleted_comment(self):
        self.assertEqual(self.product.score,2.5)
        self.new_comment.delete()
        self.assertEqual(self.product.score,4)




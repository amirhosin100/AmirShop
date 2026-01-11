from rest_framework import serializers
from apps.comment.models import Comment, CommentImage


class CommentImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentImage
        fields = [
            'image',
            'id',
        ]
        read_only_fields = ['id']


class CommentSerializer(serializers.ModelSerializer):
    images = CommentImageSerializer(many=True,read_only=True)
    class Meta:
        model = Comment
        fields = [
            'id',
            'content',
            'score',
            'images',
            'created_at',
            'updated_at',
            'status',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'status']

    def validate_score(self, score):
        if not 1 <= score <= 5:
            raise serializers.ValidationError('score must be between 1 and 5')

        return score

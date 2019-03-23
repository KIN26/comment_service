from rest_framework import serializers, pagination
from rest_framework.reverse import reverse_lazy as _

from project.apps.comment.comment_api.serializers import CommentListSerializer
from project.apps.post.models import Blog, News


fields_tuple = ('id', 'head', 'body', 'created_at')


class PostListSerializer(serializers.ModelSerializer):
    detail_url = serializers.SerializerMethodField()

    def get_detail_url(self, obj):
        return _('api:post:{0}:detail'.format(
            obj.__class__.__name__.lower()
        ), args=[obj.pk], request=self.context['request'])

    class Meta:
        fields = fields_tuple + ('detail_url',)


class BlogListSerializer(PostListSerializer):
    class Meta(PostListSerializer.Meta):
        model = Blog


class NewsListSerializer(PostListSerializer):
    class Meta(PostListSerializer.Meta):
        model = News


class PostDetailSerializer(serializers.ModelSerializer):
    comments_url = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()

    def get_comments_url(self, obj):
        return _(
            'api:comment:list',
            args=[obj.get_content_type().id, obj.id],
            request=self.context['request']
        )

    def get_comments(self, obj):
        comments = obj.comments.get_grand_parents()
        paginator = pagination.PageNumberPagination()
        page = paginator.paginate_queryset(comments, self.context['request'])
        serializer = CommentListSerializer(
            page,
            many=True,
            context=self.context
        )
        return serializer.data

    class Meta:
        fields = fields_tuple + ('comments', 'comments_url')


class NewsDetailSerializer(PostDetailSerializer):
    class Meta(PostDetailSerializer.Meta):
        model = News


class BlogDetailSerializer(PostDetailSerializer):
    class Meta(PostDetailSerializer.Meta):
        model = Blog

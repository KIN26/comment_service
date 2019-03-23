from rest_framework import serializers
from rest_framework.reverse import reverse_lazy as _

from project.apps.comment.models import Comment, CommentsReport

fields_tuple = (
    'id',
    'body',
    'user_id',
    'parent_id',
    'content_type_id',
    'object_id',
    'created_at'
)

fields_tuple_read_only = (
    'content_type_id',
    'object_id'
)


class CommentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = fields_tuple
        read_only_fields = fields_tuple_read_only


class CommentListSerializer(serializers.ModelSerializer):
    username = serializers.CharField(read_only=True, source='user.username')
    descendants_url = serializers.SerializerMethodField()
    detail_url = serializers.SerializerMethodField()
    delete_url = serializers.SerializerMethodField()
    edit_url = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()
    children_cnt = serializers.SerializerMethodField()

    def get_detail_url(self, obj):
        return _(
            'api:comment:detail',
            args=[obj.pk],
            request=self.context['request']
        )

    def get_delete_url(self, obj):
        return self.get_detail_url(obj)

    def get_edit_url(self, obj):
        return self.get_detail_url(obj)

    def get_descendants_url(self, obj):
        return _(
            'api:comment:descendants',
            args=[obj.content_type_id, obj.object_id, obj.pk],
            request=self.context['request']
        )

    def get_children_cnt(self, obj):
        if hasattr(obj, 'children'):
            return len(obj.children)
        elif hasattr(obj, 'children_cnt'):
            return obj.children_cnt
        return 0

    def get_children(self, obj):
        if hasattr(obj, 'children'):
            return self.__class__(
                obj.children.values(),
                many=True,
                context=self.context
            ).data
        return []

    class Meta:
        model = Comment
        fields = fields_tuple + (
            'username',
            'descendants_url',
            'detail_url',
            'edit_url',
            'delete_url',
            'children_cnt',
            'children'
        )
        read_only_fields = fields_tuple_read_only


class CommentReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentsReport
        fields = (
            'id',
            'filename',
            'created',
            'date_from',
            'date_till',
            'format',
            'content_type',
            'object_id'
        )
        read_only_fields = ('filename', 'created')
        extra_kwargs = {
            'format': {'write_only': True},
            'content_type': {'write_only': True},
            'object_id': {'write_only': True},
            'date_from': {'write_only': True},
            'date_till': {'write_only': True}
        }

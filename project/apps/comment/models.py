from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from reversion import register as reversion_register

from . import consts
from .managers import CommentManager


@reversion_register(fields=['body'])
class Comment(models.Model):
    parent = models.ForeignKey(
        'self',
        related_name='comment_parent',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    body = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CommentManager.as_manager()

    @classmethod
    def get_commented_ct(cls, user):
        """
        Get all content types that contain comments
        :param user: auth user instance
        :return: dict
        """
        data = ContentType.objects.filter(
            pk__in=Comment.objects.order_by().filter(
                user=user
            ).values_list('content_type').distinct()
        )
        return {i.pk: i.model_class()._meta.verbose_name for i in data}

    class Meta:
        db_table = 'comment'
        ordering = ['-created_at']


class CommentTree(models.Model):
    ancestor = models.ForeignKey(
        Comment,
        related_name='comment_tree_ancestor',
        on_delete=models.CASCADE
    )
    descendant = models.ForeignKey(
        Comment,
        related_name='comment_tree_descendant',
        on_delete=models.CASCADE
    )
    depth = models.IntegerField()

    class Meta:
        db_table = 'comment_tree'


class CommentSubscribe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()

    class Meta:
        db_table = 'comment_subscribe'
        unique_together = ['user', 'content_type', 'object_id']


class CommentsReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.ForeignKey(
        ContentType,
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    date_from = models.DateField(null=True, blank=True)
    date_till = models.DateField(null=True, blank=True)
    filename = models.FilePathField(
        path=settings.MEDIA_ROOT,
        recursive=True,
        unique=True
    )
    format = models.CharField(
        max_length=4,
        choices=consts.REPORTS_TYPE_FORMATS,
        default='json'
    )
    created = models.BooleanField(default=False)

    class Meta:
        db_table = 'comments_report'
        ordering = ['-id']

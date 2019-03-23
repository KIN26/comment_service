from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _

from project.apps.comment.models import Comment, CommentSubscribe


class AbstractPostModel(models.Model):
    head = models.CharField(max_length=100, verbose_name=_('Title'))
    body = models.TextField(verbose_name=_('Text'))
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Date of publication')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Date of update')
    )
    comments = GenericRelation(Comment)
    subscribes = GenericRelation(CommentSubscribe)

    def __str__(self):
        return self.head

    def get_content_type(self):
        """
        Get content type object by self instance
        :return: content type object
        """
        return ContentType.objects.get_for_model(self)

    @classmethod
    def get_posts_with_comments(cls, user):
        """
        Get all posts which have comments
        :param user: auth user instance
        :return: list
        """
        return list(cls.objects.annotate(
            cnt=models.Count('comments')
        ).filter(
            comments__user=user,
            cnt__gt=0
        ).values('id', 'head'))

    class Meta:
        abstract = True


class Blog(AbstractPostModel):
    class Meta:
        ordering = ['-created_at']
        db_table = 'blog'
        verbose_name = _('Blog')
        verbose_name_plural = _('Blogs')


class News(AbstractPostModel):
    class Meta:
        ordering = ['-created_at']
        db_table = 'news'
        verbose_name = _('News')
        verbose_name_plural = _('News')

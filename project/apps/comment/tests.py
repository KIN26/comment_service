import os.path
import shutil
import tempfile

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, Client, override_settings
from django.urls import reverse

from project.apps.post.models import Blog
from .exceptions import CommentTreeException
from .models import Comment, CommentTree, CommentsReport
from .utils import build_tree, get_report_filename, create_report_file


class CommentsReportsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='test_user',
            email='test@test.test',
        )
        self.user.set_password('test_pwd_123')
        self.user.save()
        self.blog = Blog.objects.create(head='t', body='t')
        self.blog_content_type = ContentType.objects.get_for_model(Blog)
        for i in range(10):
            Comment.objects.create(
                body='t{}'.format(str(i)),
                user=self.user,
                content_type_id=self.blog_content_type.pk,
                object_id=self.blog.id
            )
        self._original_media_root = settings.MEDIA_ROOT
        self._tmp_media = tempfile.mkdtemp()
        settings.MEDIA_ROOT = self._tmp_media

    def test_get_report_filename_util(self):
        filename = get_report_filename('json')
        self.assertEqual(isinstance(filename, str), True)
        self.assertEqual(len(filename) > 0, True)
        self.assertEqual(filename.find('.json') >= 0, True)

    def test_report_create_file(self):
        report = CommentsReport.objects.create(
            format='json',
            user=self.user,
            filename=get_report_filename('json')
        )
        create_report_file(report)
        self.assertEqual(os.path.isfile(
            '{0}/{1}'.format(self._tmp_media, report.filename)
        ), True)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_report_view(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('comment:reports:index'))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse('comment:reports:index'), {
            'format': 'json'
        })
        self.assertEqual(response.status_code, 400)
        response = self.client.post(reverse('comment:reports:index'), {
            'format': 'xml'
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        report = CommentsReport.objects.get(format='xml')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(os.path.isfile(
            '{0}/{1}'.format(self._tmp_media, report.filename)
        ), True)

    def test_get_content_type_objects_view(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('comment:reports:content_type_objects', kwargs={
                'content_type_id': self.blog_content_type.pk
            })
        )
        self.assertEqual(response.status_code, 400)
        response = self.client.post(
            reverse('comment:reports:content_type_objects', kwargs={
                'content_type_id': self.blog_content_type.pk
            }),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)

    def test_pagination_page(self):
        for i in range(11):
            CommentsReport.objects.create(
                format='xml',
                user=self.user,
                filename=get_report_filename('xml')
            )
        self.client.force_login(self.user)
        response = self.client.get(reverse('comment:reports:paginate', kwargs={
            'page': 2
        }))
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(self._tmp_media, ignore_errors=True)
        settings.MEDIA_ROOT = self._original_media_root
        del self._tmp_media


class CommentsTest(TestCase):
    def setUp(self):
        test_user_pwd = 'test_pwd_123'
        self.client = Client()
        self.blog_content_type_id = ContentType.objects.get_for_model(Blog).pk
        self.test_user = User.objects.create_user(
            username='test_user',
            email='nik_4design@icloud.com'
        )
        self.test_user.set_password(test_user_pwd)
        self.test_user.save()
        self.test_user_two = User.objects.create_user(
            username='test_user_two',
            email='test@test.test'
        )
        self.test_user_two.set_password(test_user_pwd)
        self.test_user_two.save()
        self.admin = User.objects.create_superuser(
            username='admin',
            email='adm@adm.adm',
            is_superuser=True,
            password=test_user_pwd
        )
        self.content_object = Blog.objects.create(
            head='Test Blog Head',
            body='Test Blog Body'
        )
        self.test_comment = Comment.objects.create(
            body='Test',
            user=self.test_user,
            content_type_id=self.blog_content_type_id,
            object_id=self.content_object.pk
        )

    def test_adding(self):
        self.assertEqual(CommentTree.objects.count(), 1)
        Comment.objects.create(
            body='Child of comment_one',
            user=self.test_user,
            content_type_id=self.blog_content_type_id,
            object_id=self.content_object.pk,
            parent=self.test_comment
        )

        self.assertEqual(CommentTree.objects.count(), 3)

    def test_deleting_object_with_child(self):
        Comment.objects.create(
            body='test',
            user=self.test_user,
            content_type_id=self.blog_content_type_id,
            object_id=self.content_object.pk,
            parent=self.test_comment
        )

        with self.assertRaises(CommentTreeException):
            self.test_comment.delete()

    def test_deleting_object_without_child(self):
        count_before = CommentTree.objects.count()
        self.test_comment.delete()
        self.assertEqual(
            CommentTree.objects.count(),
            count_before - 1
        )

    def test_getting_descendants(self):
        Comment.objects.create(
            body='test',
            user=self.test_user,
            content_type_id=self.blog_content_type_id,
            object_id=self.content_object.pk,
            parent=self.test_comment
        )
        self.assertEqual(
            Comment.objects.get_descendants(self.test_comment.pk).count(),
            1
        )

        self.assertEqual(
            Comment.objects.get_descendants(
                self.test_comment.pk,
                include_self=True
            ).count(),
            2
        )

    def test_build_tree(self):
        child = Comment.objects.create(
            body='Child of comment_one',
            user=self.test_user,
            content_type_id=self.blog_content_type_id,
            object_id=self.content_object.pk,
            parent=self.test_comment
        )
        data = Comment.objects.get_descendants(
            self.test_comment.pk,
            include_self=True
        )
        data = build_tree(data)
        self.assertEqual(isinstance(data, dict), True)
        self.assertEqual(len(data), 1)
        self.assertEqual(
            child.pk in data[self.test_comment.pk].children,
            True
        )

    def test_create_view(self):
        self.client.force_login(self.test_user)
        response = self.client.post(reverse('comment:create', kwargs={
            'content_type_id': self.blog_content_type_id,
            'object_id': self.content_object.pk
        }), {
            'body': 'test'
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(CommentTree.objects.count(), 2)
        response = self.client.post(reverse('comment:create', kwargs={
            'content_type_id': self.blog_content_type_id,
            'object_id': self.content_object.pk
        }), {
            'body': 'test'
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(CommentTree.objects.count(), 2)

    def test_update_view(self):
        self.client.force_login(self.test_user)
        response = self.client.post(reverse('comment:update', kwargs={
            'pk': self.test_comment.pk
        }), {
            'body': 'update'
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            'update',
            Comment.objects.get(pk=self.test_comment.pk).body
        )

    def test_delete_view(self):
        self.client.force_login(self.test_user_two)
        response = self.client.get(reverse('comment:delete', kwargs={
            'pk': self.test_comment.pk
        }))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            Comment.objects.filter(pk=self.test_comment.pk).exists(),
            True
        )
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('comment:delete', kwargs={
            'pk': self.test_comment.pk
        }))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            Comment.objects.filter(pk=self.test_comment.pk).exists(),
            False
        )
        parent = Comment.objects.create(
            body='Test',
            user=self.test_user,
            content_type_id=self.blog_content_type_id,
            object_id=self.content_object.pk
        )
        Comment.objects.create(
            body='Test',
            user=self.test_user,
            content_type_id=self.blog_content_type_id,
            object_id=self.content_object.pk,
            parent=parent
        )
        response = self.client.get(reverse('comment:delete', kwargs={
            'pk': parent.pk
        }))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.content,
            b"Can't delete comment with children"
        )

    def test_get_descendants_view(self):
        children = Comment.objects.create(
            body='Children',
            user=self.test_user,
            content_type_id=self.blog_content_type_id,
            object_id=self.content_object.pk,
            parent=self.test_comment
        )
        Comment.objects.create(
            body='Children 2',
            user=self.test_user,
            content_type_id=self.blog_content_type_id,
            object_id=self.content_object.pk,
            parent=children
        )
        response = self.client.get(reverse('comment:descendants', kwargs={
            'pk': self.test_comment.pk
        }), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('comment:descendants', kwargs={
            'pk': self.test_comment.pk
        }))
        self.assertEqual(response.status_code, 400)

    def test_comment_paginate_view(self):
        response = self.client.get(reverse('comment:paginate', kwargs={
            'content_type_id': self.blog_content_type_id,
            'object_id': self.content_object.pk,
            'page': 1
        }), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('comment:paginate', kwargs={
            'content_type_id': self.blog_content_type_id,
            'object_id': self.content_object.pk,
            'page': 1
        }))
        self.assertEqual(response.status_code, 400)

import os.path
import shutil
import tempfile

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test import override_settings
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from project.apps.comment.models import Comment, CommentsReport, CommentTree
from project.apps.post.models import Blog


class CommentReportApiTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test',
            email='test@test.com',
        )
        self.user.set_password('testUserPwd123')
        self.user.save()
        self.token = Token.objects.create(user=self.user)
        self.blog = Blog.objects.create(
            head='test',
            body='test'
        )
        self.ct = ContentType.objects.get_for_model(Blog)
        Comment.objects.create(
            body='test',
            user=self.user,
            content_type_id=self.ct.pk,
            object_id=self.blog.id
        )
        self._original_media_root = settings.MEDIA_ROOT
        self._tmp_media = tempfile.mkdtemp()
        settings.MEDIA_ROOT = self._tmp_media

    def test_list_method(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get(reverse('api:comment:reports'))
        self.assertEqual(response.status_code, 200)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_create_respond(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post(
            reverse('api:comment:reports'),
            {
                'format': 'xml'
            }
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual('id' in response.data, True)
        self.assertEqual(CommentsReport.objects.count(), 1)
        self.assertEqual(CommentsReport.objects.get(
            pk=response.data['id']
        ).created, True)
        self.assertEqual(os.path.isfile(
            '{0}/{1}'.format(self._tmp_media, response.data['filename'])
        ), True)

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(self._tmp_media, ignore_errors=True)
        settings.MEDIA_ROOT = self._original_media_root
        del self._tmp_media


class CommentApiTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test',
            email='test@test.com',
        )
        self.user.set_password('testUserPwd123')
        self.user.save()
        self.token = Token.objects.create(user=self.user)
        self.blog = Blog.objects.create(
            head='test',
            body='test'
        )
        self.ct = ContentType.objects.get_for_model(Blog)
        self.comment = Comment.objects.create(
            body='test',
            user=self.user,
            content_type_id=self.ct.pk,
            object_id=self.blog.id
        )

    def test_list_method(self):
        response = self.client.get(
            reverse('api:comment:list', args=(self.ct.id, self.blog.id))
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual('results' in response.data, True)
        self.assertEqual(response.data['count'], 1)

    def test_descendants_method(self):
        Comment.objects.create(
            body='test',
            user=self.user,
            content_type_id=self.ct.id,
            object_id=self.blog.id,
            parent=self.comment
        )
        response = self.client.get(
            reverse('api:comment:descendants', args=(
                self.ct.id,
                self.blog.id,
                self.comment.id
            ))
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(CommentTree.objects.count(), 3)

    def test_create_method(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post(
            reverse('api:comment:list', args=(self.ct.id, self.blog.id)),
            {
                'body': 'test create'
            },
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual('id' in response.data, True)
        self.assertEqual(Comment.objects.count(), 2)
        self.assertEqual(CommentTree.objects.count(), 2)

    def test_update_method(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.put(
            reverse('api:comment:detail', args=(self.comment.id,)),
            {
                'body': 'updated'
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['body'], 'updated')

    def test_delete_method(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.delete(
            reverse('api:comment:detail', args=(self.comment.id,))
        )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Comment.objects.count(), 0)
        self.assertEqual(CommentTree.objects.count(), 0)

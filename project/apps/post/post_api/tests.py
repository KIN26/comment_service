from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from rest_framework.test import APITestCase

from project.apps.post.models import Blog


class PostApiTestCase(APITestCase):
    def setUp(self):
        self.blog = Blog.objects.create(
            head='test',
            body='test'
        )
        self.content_type = ContentType.objects.get_for_model(
            Blog
        )

    def test_list_method(self):
        response = self.client.get(
            reverse('api:post:blog:list')
        )
        self.assertEqual(response.status_code, 200)

    def test_detail_method(self):
        response = self.client.get(
            reverse('api:post:blog:detail', args=(self.blog.pk,))
        )
        self.assertEqual(response.status_code, 200)

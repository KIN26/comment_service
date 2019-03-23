from django.test import TestCase, Client
from django.urls import reverse

from .models import Blog


class PostPageTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.single_post = Blog.objects.create(
            head='Test',
            body='Test'
        )

    def test_list_page(self):
        response = self.client.get(reverse('post:blog:list'))
        self.assertEqual(response.status_code, 200)

    def test_detail_page(self):
        response = self.client.get(reverse('post:blog:detail', kwargs={
            'pk': self.single_post.pk
        }))
        self.assertEqual(response.status_code, 200)

    def test_pagination_page(self):
        for i in range(11):
            Blog.objects.create(head=str(i), body=str(i))
        response = self.client.get(reverse('post:blog:pagination', kwargs={
            'page': 2
        }))
        self.assertEqual(response.status_code, 200)

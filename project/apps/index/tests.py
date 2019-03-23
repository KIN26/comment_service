from django.test import TestCase, Client
from django.urls import reverse


class IndexPageTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_response(self):
        response = self.client.get(reverse('index_page'))
        self.assertEqual(response.status_code, 200)

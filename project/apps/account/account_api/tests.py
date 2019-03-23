from django.contrib.auth.models import User
from django.core import mail
from django.test import override_settings
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

AUTH_DATA = ('username', 'userpwd123', 'user@test.ru')


class AccountApiTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username=AUTH_DATA[0],
            email=AUTH_DATA[2]
        )
        self.user.set_password(AUTH_DATA[1])
        self.user.save()
        self.token = Token.objects.create(user=self.user)

    def test_login(self):
        response = self.client.post(
            reverse('api:account:rest_login'),
            {
                'username': AUTH_DATA[0],
                'password': AUTH_DATA[1]
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual('key' in response.data, True)
        self.assertEqual(isinstance(response.data['key'], str), True)

    def test_logout(self):
        response = self.client.post(
            reverse('api:account:rest_logout'),
            headers={
                'Authorization': 'Token %s' % self.token
            }
        )
        self.assertEqual(response.status_code, 200)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_register(self):
        response = self.client.post(
            reverse('api:account:register'),
            {
                'username': 'nikita',
                'password': 'NIK123pwd',
                'email': 'nik_4design@icloud.com'
            }
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual('id' in response.data, True)
        self.assertEqual(User.objects.all().count(), 2)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject,
            'Registration on the comment service'
        )

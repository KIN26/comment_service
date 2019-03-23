from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase

from .models import AccountTokens
from .tasks import send_activation_token


class AccountTest(TestCase):
    def setUp(self):
        self.test_user = User.objects.create_user(
            username='test_user',
            email='test@mail.com'
        )
        self.test_user.set_password('test_user1pwd')
        self.test_user.save()

    def test_user_activate(self):
        token = AccountTokens(token='123', user=self.test_user)
        token.save()
        AccountTokens.user_activate(token.token)

        with self.assertRaises(AccountTokens.DoesNotExist):
            AccountTokens.objects.get(token=token.token)
        self.assertEqual(self.test_user.is_active, True)

    def test_create_token(self):
        token_data = AccountTokens.get_activation_data(self.test_user)
        self.assertEqual(
            AccountTokens.objects.get(token=token_data['token']).token,
            token_data['token']
        )

    def test_send_token(self):
        send_activation_token.apply(args=('http://localhost:8000/', {
            'token': '123',
            'username': 'nikita',
            'email': 'nik_4design@icloud.com'
        })).get()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject,
            'Registration on the comment service'
        )

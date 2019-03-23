from hashlib import sha1 as sha

from django.contrib.auth.models import User
from django.db import models


class AccountTokens(models.Model):
    token = models.CharField(max_length=40, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def get_activation_data(cls, user):
        token = sha()
        token.update(str(user.username).encode('utf-8'))
        obj = cls(token=token.hexdigest(), user=user)
        obj.save()
        return {
            'username': user.username,
            'email': user.email,
            'token': obj.token
        }

    @classmethod
    def user_activate(cls, token):
        obj = cls.objects.get(token=token)
        obj.user.is_active = True
        obj.user.save()
        obj.delete()

    class Meta:
        db_table = 'account_tokens'

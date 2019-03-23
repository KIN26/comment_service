from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from project.celery import app


@app.task(bind=True, ignore_result=True)
def send_activation_token(self, host, data):
    send_mail(
        _('Registration on the comment service'),
        '',
        settings.EMAIL_HOST_USER,
        [data['email']],
        html_message=render_to_string('account/email.html', {
            'username': data['username'],
            'token': data['token'],
            'url': host + reverse('account:activate')
        })
    )

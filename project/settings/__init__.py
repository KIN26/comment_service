from __future__ import absolute_import

import os

from split_settings.tools import optional, include

ENV = os.environ.get('DJANGO_ENV', 'dev')

include(
    'base.py',
    '%s/channels.py' % ENV,
    '%s/database.py' % ENV,
    '%s/celery.py' % ENV,
    'email.py',
    'rest_framework.py'
)

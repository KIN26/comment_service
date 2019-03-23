"""
    Database settings
"""

DATABASES = {
    'default': {
        'NAME': 'comment_service',
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'root',
        'PASSWORD': '1234',
        'HOST': 'db',
        'OPTIONS': {
            'autocommit': True
        },
    }
}

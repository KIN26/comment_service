import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SECRET_KEY = '+6gb-m)uth=$uqx+lqh%_=o7kie@_yu99_tuznuej%%-8^3^%('
DEBUG = True
ALLOWED_HOSTS = []
LANGUAGE_CODE = 'en'
LANGUAGES = (('en', 'English'),)
LOCALE_PATHS = (os.path.join(BASE_DIR, 'locale'),)
INSTALLED_APPS = [
    'channels',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_auth',
    'reversion',
    'project',
    'project.apps.post.apps.PostConfig',
    'project.apps.post.templatetags',
    'project.apps.index.apps.IndexConfig',
    'project.apps.account.apps.AccountConfig',
    'project.apps.comment.apps.CommentConfig',
    'project.apps.post.post_api.apps.PostApiConfig',
    'project.apps.account.account_api.apps.AccountApiConfig',
    'project.apps.comment.comment_api.apps.CommentApiConfig'
]
MIDDLEWARE = [
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'reversion.middleware.RevisionMiddleware'
]
ROOT_URLCONF = 'project.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
            ],
        },
    },
]
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'
WSGI_APPLICATION = 'project.wsgi.application'
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
TIME_ZONE = 'Asia/Almaty'
DATE_FORMAT = "d.m.y"
USE_I18N = True
USE_L10N = True
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)
STATIC_ROOT = os.path.join(BASE_DIR, 'static/collect')
LOGIN_REDIRECT_URL = 'index_page'
LOGOUT_REDIRECT_URL = 'index_page'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

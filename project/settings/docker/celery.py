"""
    Celery settings
"""

from kombu import Queue, Exchange

CELERY_BROKER_URL = 'amqp://guest:guest@rabbitmq:5672//'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_RESULT_BACKEND = "redis"
CELERY_REDIS_HOST = "redis"
CELERY_REDIS_PORT = 6379
CELERY_REDIS_DB = 2
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Almaty'
CELERY_TASK_QUEUES = (
    Queue('high', Exchange('high'), routing_key='high'),
    Queue('normal', Exchange('normal'), routing_key='normal'),
    Queue('low', Exchange('low'), routing_key='low')
)
CELERY_TASK_ROUTES = {
    'project.apps.account.tasks.send_activation_token': {
        'queue': 'low',
        'routing_key': 'low'
    },
    'project.apps.comment.tasks.get_report_file': {
        'queue': 'normal',
        'routing_key': 'normal'
    },
}
CELERY_DEFAULT_QUEUE = 'normal'
CELERY_DEFAULT_EXCHANGE = 'normal'
CELERY_DEFAULT_ROUTING_KEY = 'normal'

from django.apps import AppConfig


class CommentConfig(AppConfig):
    name = 'project.apps.comment'
    verbose_name = 'Comment'

    def ready(self):
        from project.apps.comment.signals import handlers

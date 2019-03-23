from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path

from project.apps.comment.consumers import CommentNotificationConsumer

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter([
            path(
                'comment/notification/',
                CommentNotificationConsumer,
                name='notifications'
            )
        ])
    )
})

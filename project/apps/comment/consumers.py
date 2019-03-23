from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from .models import CommentSubscribe


class CommentNotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        if not self.scope['user'].is_anonymous:
            await self.accept()
            groups = await database_sync_to_async(
                self.get_users_subscription
            )()
            await self.add_subscriptions(groups)
            await self.channel_layer.group_add(
                'user_{0}'.format(self.scope['user'].id),
                self.channel_name
            )
            await self.send_json({
                'action': 'init',
                'data': {
                    'user_id': self.scope['user'].id
                }
            })
        else:
            await self.close()

    async def add_subscriptions(self, groups):
        for group in groups:
            await self.channel_layer.group_add(
                'post_{0}_{1}'.format(
                    group.content_type_id,
                    group.object_id
                ),
                self.channel_name
            )

    async def receive_json(self, content, **kwargs):
        command = content.get('command', None)
        data = content.get('data', dict())
        if command == 'subscribe':
            await self.subscribe(data)
        elif command == 'unsubscribe':
            await self.unsubscribe(data)
        else:
            await self.send_json({
                'error': 'unknown command'
            })

    async def send_notification(self, data):
        await self.send_json(data)

    async def subscribe(self, data):
        await self.channel_layer.group_add(
            'post_{content_type_id}_{object_id}'.format(
                **data
            ),
            self.channel_name
        )
        await database_sync_to_async(self.save_subscribe)(
            data['content_type_id'],
            data['object_id']
        )
        await self.send_json({
            'action': 'unsubscribe'
        })

    async def unsubscribe(self, data):
        await self.channel_layer.group_discard(
            'post_{content_type_id}_{object_id}'.format(
                **data
            ),
            self.channel_name
        )
        await database_sync_to_async(self.delete_subscribe)(
            data['content_type_id'],
            data['object_id']
        )
        await self.send_json({
            'action': 'subscribe'
        })

    def save_subscribe(self, content_type_id, object_id):
        return CommentSubscribe.objects.create(
            content_type_id=content_type_id,
            object_id=object_id,
            user=self.scope['user']
        )

    def delete_subscribe(self, content_type_id, object_id):
        return CommentSubscribe.objects.get(
            content_type_id=content_type_id,
            object_id=object_id,
            user=self.scope['user']
        ).delete()

    def get_users_subscription(self):
        return CommentSubscribe.objects.filter(
            user=self.scope['user']
        )

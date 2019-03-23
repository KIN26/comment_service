from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils.translation import ugettext as _


def send_report_notification(user_id, report_id):
    channel_layer = get_channel_layer()
    group_name = 'user_{}'.format(user_id)
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'send.notification',
            'action': 'report_created',
            'data': {
                'id': report_id
            }
        }
    )


def send_notification(action, sender, comment):
    messages = {
        'delete': _('To the post to which you subscribed was deleted '
                    'comment'),
        'update': _('To the post to which you subscribed was edited '
                    'comment'),
        'create': _('To the post to which you subscribed was created '
                    'comment')
    }
    channel_layer = get_channel_layer()
    group_name = 'post_{0}_{1}'.format(
        comment['content_type_id'],
        comment['object_id']
    )
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'send.notification',
            'action': action,
            'data': {
                'msg': messages[action],
                'body': comment['body'],
                'sender': sender
            }
        }
    )

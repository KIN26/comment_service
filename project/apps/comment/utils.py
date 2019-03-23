import uuid

from django.conf import settings
from django.core import serializers

from .models import Comment


def build_tree(data, parent=None):
    """
    Return list of comments as tree
    :param data: queryset
    :param parent: int
    :return: list
    """
    if not data.exists():
        return dict()
    data = dict(zip([i.id for i in data], data))
    for pk, item in data.items():
        if item.parent_id in data:
            if not hasattr(data[item.parent_id], 'children'):
                data[item.parent_id].children = dict()
            data[item.parent_id].children[pk] = item
    return {i.id: i for i in data.values() if i.parent_id == parent}


def get_report_filename(ext):
    """
    Create uniq filename
    :param ext: string
    :return: string
    """
    return '{0}.{1}'.format(str(uuid.uuid4()).lower(), ext)


def create_report_file(report_obj):
    """
    Create a file with the specified extension
    :param report_obj: CommentReport instance
    :return: void
    """
    filters = dict()
    if report_obj.date_from is not None:
        filters['created_at__gte'] = report_obj.date_from
    if report_obj.date_till is not None:
        filters['created_at__lte'] = report_obj.date_till
    if report_obj.content_type_id is not None:
        filters['content_type_id'] = report_obj.content_type_id
    if report_obj.object_id is not None:
        filters['object_id'] = report_obj.object_id
    qs = Comment.objects.filter(user=report_obj.user, **filters)
    filepath = '{0}/{1}'.format(settings.MEDIA_ROOT, report_obj.filename)
    content = serializers.serialize(report_obj.format, qs)
    with open(filepath, 'wb+') as f:
        f.write(content.encode('utf-8'))

# templatetags/post_tags.py

from django.template import Library

register = Library()


@register.filter
def brief(body, length=100):
    if len(body) < length:
        return body[0:length]
    return body[0:length] + '...'

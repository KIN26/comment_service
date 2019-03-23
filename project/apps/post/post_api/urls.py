from django.urls import path, include

from project.apps.post.models import Blog, News
from . import views

app_name = 'post_api'
urlpatterns = [
    path('blogs/', include(([
        path(
            'list/',
            views.PostList.as_view(
                queryset=Blog.objects.all()
            ),
            name='list'
        ),
        path(
            'detail/<int:pk>',
            views.PostDetail.as_view(
                queryset=Blog.objects.all()
            ),
            name='detail'
        )
    ], 'blog'), namespace='blog')),
    path('news/', include(([
        path(
            'list/',
            views.PostList.as_view(
                queryset=News.objects.all()
            ),
            name='list'
        ),
        path(
            'detail/<int:pk>',
            views.PostDetail.as_view(
                queryset=News.objects.all()
            ),
            name='detail'
        )
    ], 'news'), namespace='news')),
]

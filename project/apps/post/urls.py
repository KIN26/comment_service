from django.urls import path, include

from .models import Blog, News
from .views import BlogList, NewsList, PostDetail

app_name = 'post'
urlpatterns = [
    path('blog/', include(([
        path(
            '',
            BlogList.as_view(),
            name='list'
        ),
        path(
            '<int:pk>/',
            PostDetail.as_view(model=Blog),
            name='detail'
        ),
        path(
            'page/<int:page>/',
            BlogList.as_view(),
            name='pagination'
        )
    ], 'blog'), namespace='blog')),
    path('news/', include(([
        path(
            '',
            NewsList.as_view(),
            name='list'
        ),
        path(
            '<int:pk>/',
            PostDetail.as_view(model=News),
            name='detail'
        ),
        path(
            'page/<int:page>/',
            NewsList.as_view(),
            name='pagination'
        )
    ], 'news'), namespace='news'))
]

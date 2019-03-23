from django.urls import path

from . import views

app_name = 'comment_api'
urlpatterns = [
    path(
        'list/<int:content_type_id>/<int:object_id>',
        views.CommentsListView.as_view(),
        name='list'
    ),
    path(
        'list/<int:content_type_id>/<int:object_id>/<int:parent_id>',
        views.CommentsListView.as_view(),
        name='descendants'
    ),
    path(
        'detail/<int:pk>',
        views.CommentEditDeleteView.as_view(),
        name='detail'
    ),
    path(
        'reports/list',
        views.CommentsReportView.as_view(),
        name='reports'
    )
]

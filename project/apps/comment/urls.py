from django.contrib.auth.decorators import login_required
from django.urls import path, include

from . import views

app_name = 'comment'
urlpatterns = [
    path(
        'create/<int:content_type_id>/<int:object_id>/',
        login_required(views.CreateComment.as_view()),
        name='create'
    ),
    path(
        'update/<int:pk>/',
        login_required(views.UpdateComment.as_view()),
        name='update'
    ),
    path(
        'delete/<int:pk>/',
        login_required(views.DeleteComment.as_view()),
        name='delete'
    ),
    path(
        'descendants/<int:pk>/',
        views.GetCommentDescendants.as_view(),
        name='descendants'
    ),
    path(
        'page/<int:content_type_id>/<int:object_id>/<int:page>/',
        views.GetCommentPage.as_view(),
        name='paginate'
    ),
    path('reports/', include(([
        path(
            '',
            login_required(views.CommentReportView.as_view()),
            name='index'
        ),
        path(
            'page/<int:page>/',
            login_required(views.CommentReportView.as_view()),
            name='paginate'
        ),
        path(
            'content_type_objects/<int:content_type_id>/',
            login_required(views.CommentsContentTypeObjects.as_view()),
            name='content_type_objects'
        )
    ], 'reports'), namespace='reports'))
]

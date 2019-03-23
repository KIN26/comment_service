import reversion
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated

from project.apps.comment.exceptions import CommentTreeException
from project.apps.comment.models import Comment, CommentsReport
from project.apps.comment.notify import send_notification
from project.apps.comment.tasks import get_report_file
from project.apps.comment.utils import build_tree, get_report_filename
from . import permissions, serializers


class CommentsListView(generics.ListCreateAPIView):
    """
    List of all comments, comment's descendants list, create a new comment.
    """
    serializer_class = serializers.CommentListSerializer
    permission_classes = (IsAuthenticated | permissions.ReadOnly,)

    def get_queryset(self):
        if self.kwargs.get('parent_id'):
            return list(build_tree(
                Comment.objects.get_descendants(self.kwargs['parent_id']),
                parent=self.kwargs['parent_id']
            ).values())
        return Comment.objects.get_grand_parents(**self.kwargs)

    def list(self, request, *args, **kwargs):
        if self.kwargs.get('parent_id'):
            self._paginator = None
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, **self.kwargs)
        send_notification('create', self.request.user.id, serializer.data)
        reversion.set_comment('create')


class CommentEditDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """
    Update or delete comment
    """
    permission_classes = (IsAuthenticated | permissions.ReadOnly,)
    serializer_class = serializers.CommentDetailSerializer
    queryset = Comment.objects.all()

    def perform_update(self, serializer):
        serializer.save()
        send_notification('update', self.request.user.id, serializer.data)
        reversion.set_comment('update')

    def perform_destroy(self, instance):
        try:
            deleted_instance = instance.__dict__
            instance.delete()
            send_notification('update', self.request.user.id, deleted_instance)
        except CommentTreeException as e:
            raise ValidationError(e.message)


class CommentsReportView(generics.ListCreateAPIView):
    """
    List reports or create a new report
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.CommentReportSerializer

    def get_queryset(self):
        return CommentsReport.objects.filter(
            user=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            filename=get_report_filename(self.request.POST.get('format'))
        )
        get_report_file.apply_async((serializer.data['id'],), countdown=1)

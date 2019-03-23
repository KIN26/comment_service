from reversion import set_comment
from reversion.views import RevisionMixin
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse, response, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView

from . import consts
from .exceptions import CommentTreeException
from .mixins import IsAjaxMixin
from .models import Comment, CommentsReport
from .notify import send_notification
from .tasks import get_report_file
from .utils import build_tree, get_report_filename


class CreateComment(IsAjaxMixin, RevisionMixin, CreateView):
    """
    Create a new comment
    """
    model = Comment
    fields = ['body', 'parent']
    template_name = 'comment/partials/item.html'
    http_method_names = ['post']

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.user = self.request.user
        comment.content_type_id = self.kwargs['content_type_id']
        comment.object_id = self.kwargs['object_id']
        self.object = form.save()
        set_comment('create')
        send_notification('create', self.request.user.id, self.object.__dict__)
        return self.render_to_response({
            'item': self.object
        })


class UpdateComment(IsAjaxMixin, RevisionMixin, UpdateView):
    """
    Update existing comment
    """
    model = Comment
    fields = ['body']
    http_method_names = ['post']

    def get_object(self, queryset=None):
        comment = get_object_or_404(Comment, pk=self.kwargs['pk'])
        if comment.user == self.request.user or self.request.user.is_superuser:
            return comment
        raise PermissionDenied

    def form_valid(self, form):
        self.object = form.save()
        set_comment('update')
        send_notification('update', self.request.user.id, self.object.__dict__)
        return JsonResponse({
            'status': 'success'
        })


class DeleteComment(DeleteView):
    """
    Delete comment instance
    """
    model = Comment

    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        user = self.object.user
        if user == self.request.user or self.request.user.is_superuser:
            try:
                self.object.delete()
                send_notification(
                    'delete',
                    request.user.id,
                    self.object.__dict__
                )
            except CommentTreeException as e:
                return response.HttpResponseBadRequest(e.message)
        else:
            raise PermissionDenied
        messages.success(
            self.request,
            _('Comment has been deleted')
        )
        return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))


class GetCommentDescendants(IsAjaxMixin, TemplateView):
    """
    Get all descendants of the instance
    """
    template_name = 'comment/node.html'
    http_method_names = ['get']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['data'] = build_tree(
            Comment.objects.get_descendants(
                self.kwargs['pk']
            ).select_related('user'),
            self.kwargs['pk']
        )
        return context


class GetCommentPage(IsAjaxMixin, ListView):
    """
    Get paginated comment list
    """
    paginate_by = consts.PAGINATE_BY
    model = Comment
    context_object_name = "data"
    template_name = 'comment/list.html'
    http_method_names = ['get']

    def get_queryset(self):
        return super().get_queryset().get_grand_parents(
            object_id=self.kwargs['object_id'],
            content_type_id=self.kwargs['content_type_id'],
        ).select_related('user')


class CommentReportView(CreateView, ListView):
    """
    List all comment reports or create a new comment report
    """
    model = CommentsReport
    paginate_by = consts.REPORTS_PAGINATE_BY
    context_object_name = 'archive'
    fields = ['date_from', 'date_till', 'content_type', 'object_id', 'format']
    template_name = 'comment/reports.html'

    def dispatch(self, request, *args, **kwargs):
        if request.method == 'POST' and not request.is_ajax():
            return response.HttpResponseBadRequest()
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.model.objects.filter(
            user=self.request.user
        )

    def get_context_data(self, **kwargs):
        kwargs['formats'] = consts.REPORTS_TYPE_FORMATS
        kwargs['content_types'] = Comment.get_commented_ct(self.request.user)
        return super().get_context_data(**kwargs)

    def form_invalid(self, form):
        return JsonResponse({
            'msg': 'error'
        })

    def form_valid(self, form):
        report = form.save(commit=False)
        report.user = self.request.user
        report.filename = get_report_filename(report.format)
        report.save()
        get_report_file.apply_async((report.id,), countdown=1)
        return JsonResponse({
            'html': render_to_string('comment/partials/archive_item.html', {
                'item': report
            })
        })


class CommentsContentTypeObjects(View):
    """
    List of content types that contain comments
    """
    def post(self, *args, **kwargs):
        if not self.request.is_ajax():
            return response.HttpResponseBadRequest()
        return JsonResponse({
            'data': ContentType.objects.get(
                pk=self.kwargs['content_type_id']
            ).model_class().get_posts_with_comments(self.request.user)
        })

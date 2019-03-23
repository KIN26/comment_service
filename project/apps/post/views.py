from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.utils.translation import ugettext_lazy as _
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from project.apps.comment import consts as comment_consts
from .models import Blog, News


class BlogList(ListView):
    """
    List all blogs with pagination
    """
    model = Blog
    template_name = 'post/list.html'
    paginate_by = 10
    context_object_name = 'posts'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['item_url'] = '{0}:detail'.format(
            self.request.resolver_match.namespace,
        )
        context['paginate_url'] = '{0}:pagination'.format(
            self.request.resolver_match.namespace,
        )
        context['page_title'] = _('Blogs')
        context['title'] = _('List of blogs')
        return context


class NewsList(BlogList):
    """
    List all news with pagination
    """
    model = News

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('News')
        context['title'] = _('List of news')
        return context


class PostDetail(DetailView):
    """
    Blog and News detail view
    """
    template_name = 'post/detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        content_type_obj = ContentType.objects.get_for_model(self.model)
        comments_list = context['object'].comments.get_grand_parents() \
            .select_related('user')
        paginator = Paginator(comments_list, comment_consts.PAGINATE_BY)
        context['comments'] = paginator.get_page(1)
        context['content_type_id'] = content_type_obj.pk
        if self.request.user.is_authenticated:
            context['subscribe'] = context['object'].subscribes.filter(
                user=self.request.user
            ).exists()
        return context

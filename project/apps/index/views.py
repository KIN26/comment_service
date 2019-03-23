from django.views.generic.base import TemplateView

from project.apps.post.models import Blog, News


class IndexPageView(TemplateView):
    """
    Index page view with last five blogs and news
    """
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['blogs'] = Blog.objects.all()[0:5]
        context['news'] = News.objects.all()[0:5]
        return context

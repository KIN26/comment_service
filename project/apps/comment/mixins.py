from django.http import response


class IsAjaxMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.is_ajax():
            return response.HttpResponseBadRequest()
        return super().dispatch(request, *args, **kwargs)

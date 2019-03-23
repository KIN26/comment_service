from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import View
from django.views.generic.edit import CreateView

from .forms import CustomAccountRegisterForm, CustomLoginForm
from .models import AccountTokens
from .tasks import send_activation_token


class RegistrationAccountView(CreateView):
    """
    Create a new user
    """
    form_class = CustomAccountRegisterForm
    template_name = 'account/register.html'
    success_url = reverse_lazy('account:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        send_activation_token.delay(
            self.request.get_host(),
            AccountTokens.get_activation_data(form.instance)
        )
        messages.success(self.request, _("Your account was created "
                                         "successfully, the link to its "
                                         "activation was sent to your email"))
        return response


class LoginAccountView(LoginView):
    """
    User login
    """
    form_class = CustomLoginForm
    template_name = 'account/login.html'


class AccountActivation(View):
    """
    Activate user
    """

    def get(self, request):
        try:
            AccountTokens.user_activate(request.GET.get('token', None))
        except AccountTokens.DoesNotExist:
            messages.error(self.request, _('Activation error'))
        else:
            messages.success(self.request, _('Your account is activated'))
        return HttpResponseRedirect(reverse_lazy('account:login'))

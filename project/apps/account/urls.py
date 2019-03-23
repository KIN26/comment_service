from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = 'account'
urlpatterns = [
    path(
        'login/',
        views.LoginAccountView.as_view(),
        name='login'
    ),
    path(
        'register/',
        views.RegistrationAccountView.as_view(),
        name='register'
    ),
    path(
        'logout/',
        LogoutView.as_view(),
        name='logout'
    ),
    path(
        'activate/',
        views.AccountActivation.as_view(),
        name='activate'
    )
]

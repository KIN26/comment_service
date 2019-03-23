from django.urls import path, include

from . import views

app_name = 'account_api'
urlpatterns = [
    path('auth/', include('rest_auth.urls')),
    path(
        'register/',
        views.RegistrationView.as_view(),
        name='register'
    ),
]

from django.contrib.auth.models import User
from rest_framework.generics import CreateAPIView

from project.apps.account.models import AccountTokens
from project.apps.account.tasks import send_activation_token
from .serializers import RegistrationSerializer


class RegistrationView(CreateAPIView):
    """
    Create a new user
    """
    serializer_class = RegistrationSerializer
    queryset = User.objects.all()

    def perform_create(self, serializer):
        instance = serializer.save()
        send_activation_token.delay(
            self.request.get_host(),
            AccountTokens.get_activation_data(instance)
        )

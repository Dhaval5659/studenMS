from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from ..models import User
from ..permissions import IsAdmin
from ..serializers import userSerializers
from ..utils import StandardResponseMixin


class UserViewSet(StandardResponseMixin, viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = userSerializers
    permission_classes = [IsAuthenticated, IsAdmin]

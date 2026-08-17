# api/views/role_views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from ..models import Role
from ..serializers import roleSerializer
from ..permissions import IsAdmin
from ..utils import StandardResponseMixin


class RoleViewSet(StandardResponseMixin, viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = roleSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

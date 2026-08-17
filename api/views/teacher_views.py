from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated

from ..models import Teacher
from ..permissions import IsOwnerOrAdmin, get_role_name
from ..serializers import teacherSerializer, teacherRegisterSerializer
from ..utils import StandardResponseMixin


class TeacherViewSet(StandardResponseMixin, viewsets.ModelViewSet):
    serializer_class = teacherSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_serializer_class(self):
        if self.action == 'create':
            role_name = get_role_name(self.request.user)
            if role_name == 'Admin':
                return teacherRegisterSerializer
            return teacherSerializer
        return teacherSerializer

    def get_queryset(self):
        user = self.request.user
        role_name = get_role_name(user)

        if role_name == 'Admin':
            return Teacher.objects.all()
        if role_name == 'Teacher':
            return Teacher.objects.filter(user=user)
        return Teacher.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        role_name = get_role_name(user)

        if role_name == 'Admin':
            serializer.save()
        elif role_name == 'Teacher':
            if Teacher.objects.filter(user=user).exists():
                raise ValidationError({'user': 'You already have a teacher profile.'})
            serializer.save(user=user)
        else:
            raise PermissionDenied("You don't have permission to create a teacher record.")

    def perform_update(self, serializer):
        user = self.request.user
        if get_role_name(user) == 'Admin':
            serializer.save()
        else:
            serializer.save(user=user)

    def perform_destroy(self, instance):
        instance.user.delete()

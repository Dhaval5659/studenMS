from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated

from ..models import Student
from ..permissions import IsStudentOwnerAdminOrTeacherReadOnly, get_role_name
from ..serializers import studentSerializer, studentRegisterSerializer
from ..utils import StandardResponseMixin


class StudentViewSet(StandardResponseMixin, viewsets.ModelViewSet):
    serializer_class = studentSerializer
    permission_classes = [IsAuthenticated, IsStudentOwnerAdminOrTeacherReadOnly]

    def get_serializer_class(self):
        if self.action == 'create':
            role_name = get_role_name(self.request.user)
            if role_name == 'Admin':
                return studentRegisterSerializer
            return studentSerializer
        return studentSerializer

    def get_queryset(self):
        user = self.request.user
        role_name = get_role_name(user)
        if role_name == 'Admin':
            return Student.objects.all()
        if role_name == 'Teacher':
            return Student.objects.all()
        if role_name == 'Student':
            return Student.objects.filter(user=user)
        return Student.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        role_name = get_role_name(user)

        if role_name == 'Admin':
            serializer.save()
        elif role_name == 'Student':
            if Student.objects.filter(user=user).exists():
                raise ValidationError({'user': 'You already have a student profile.'})
            serializer.save(user=user)
        else:
            raise PermissionDenied("You don't have permission to create a student record.")

    def perform_update(self, serializer):
        user = self.request.user
        role_name = get_role_name(user)

        if role_name == 'Admin':
            serializer.save()
        elif role_name == 'Teacher':
            serializer.save(user=serializer.instance.user)
        else:
            serializer.save(user=user)

    def perform_destroy(self, instance):
        instance.user.delete()

from rest_framework.permissions import BasePermission, SAFE_METHODS


def get_role_name(user):
    role = getattr(user, 'role', None)
    return getattr(role, 'role_name', None)


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and get_role_name(request.user) == 'Admin'
        )


class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and get_role_name(request.user) == 'Teacher'
        )


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and get_role_name(request.user) == 'Student'
        )


class IsOwnerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if get_role_name(request.user) == 'Admin':
            return True
        return obj.user_id == request.user.id


class IsTeacherOwnerAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        role_name = get_role_name(request.user)
        return role_name in ['Admin', 'Teacher']

    def has_object_permission(self, request, view, obj):
        role_name = get_role_name(request.user)
        if role_name == 'Admin':
            return True
        if role_name == 'Teacher' and request.method in SAFE_METHODS:
            return True
        return obj.user_id == request.user.id


class IsStudentOwnerAdminOrTeacherReadOnly(BasePermission):
    def has_permission(self, request, view):
        role_name = get_role_name(request.user)
        if role_name == 'Admin':
            return True                              # Admin: full access, any action
        if role_name == 'Teacher':
            return True                              # Teacher: full access to student records
        if role_name == 'Student':
            return True                              # Student: can attempt any action (further restricted at object level)
        return False                                 # anyone else (unauthenticated, no role): blocked entirely
        
    
    def has_object_permission(self, request, view, obj):
        role_name = get_role_name(request.user)
        if role_name == 'Admin':
            return True
        if role_name == 'Teacher':
            return True
        return obj.user_id == request.user.id   # Student: only their own object

    

from django.contrib import admin
from .models import User, Student, Role, Teacher

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['id', 'role_name']


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_name', 'email', 'role']
    list_filter = ['role']
    search_fields = ['user_name', 'email']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'roll_no', 'std']
    list_filter = ['std']
    search_fields = ['user__user_name', 'roll_no']


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'subject']
    list_filter = ['subject']
    search_fields = ['user__user_name', 'subject']
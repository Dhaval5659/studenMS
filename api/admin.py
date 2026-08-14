from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User, Student, Role, Teacher

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['id', 'role_name']


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ['id', 'username', 'email', 'role']
    list_filter = ['role']
    search_fields = ['username', 'email']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'roll_no', 'std']
    list_filter = ['std']
    search_fields = ['user__username', 'roll_no']


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'subject']
    list_filter = ['subject']
    search_fields = ['user__username', 'subject']
# urls.py
from django.urls import path, include
from .views.auth_views import CustomTokenRefreshView, login_api, register_api, logout_api, forgot_password_api, reset_password_api
from rest_framework.routers import DefaultRouter
from .views.student_views import StudentViewSet
from .views.teacher_views import TeacherViewSet
from .views.user_views import UserViewSet
from .views.role_views import RoleViewSet

router = DefaultRouter()
router.register('students', StudentViewSet, basename='student')
router.register('teachers', TeacherViewSet, basename='teacher')
router.register('users', UserViewSet, basename='user')
router.register('roles', RoleViewSet, basename='role')

urlpatterns = [
    path('register/', register_api, name='register'),
    path('login/', login_api, name='login'),
    path('logout/', logout_api, name = 'logout'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
    path('forgot-password/', forgot_password_api, name='forgot_password'),
    path('reset-password/', reset_password_api, name='reset_password'),
]

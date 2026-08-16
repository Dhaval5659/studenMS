from django.urls import path
from .views.auth_views import login_api, register_api
from .views.student_views import student_api
from .views.teacher_views import teacher_api
from .views.user_views import user_api
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('register/', register_api, name='register'),
    path('login/', login_api, name='login'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('users/', user_api, name='user-list'),
    path('users/<int:pk>/', user_api, name='user-detail'),
    path('students/', student_api, name='student-list'),
    path('students/<int:pk>/', student_api, name='student-detail'),
    path('teachers/', teacher_api, name='teacher-list'),
    path('teachers/<int:pk>/', teacher_api, name='teacher-detail'),
]

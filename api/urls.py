from django.urls import path
from api.views import login_api, register_api, student_api, teacher_api, user_api
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('users/', user_api, name='user-list'),
    path('users/<int:pk>/', user_api, name='user-detail'),
    path('register/', register_api, name='register'),
    path('login/', login_api, name='login'),
    path('students/', student_api, name='student-list'),
    path('students/<int:pk>/', student_api, name='student-detail'),
    path('teachers/', teacher_api, name='teacher-list'),
    path('teachers/<int:pk>/', teacher_api, name='teacher-detail'),
]

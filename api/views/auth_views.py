from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenRefreshView
from ..models import User
from ..serializers import registerSerializer, userSerializers
from ..utils import error_response, success_response
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError


@api_view(['POST'])
@permission_classes([AllowAny])
def register_api(request):
    if request.method == 'POST':
        serializer = registerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success_response(serializer.data, 'Data created successfully', status.HTTP_201_CREATED)
        return error_response(serializer.errors, 'Validation failed', status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_api(request):
    if request.method == 'POST':
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return error_response(
                {'error': 'Email and password both are required'},
                'Validation failed',
                status.HTTP_400_BAD_REQUEST,
            )

        try:
            user_obj = User.objects.get(email=email)   # lookup by email ONLY, no password
        except User.DoesNotExist:
            return error_response(
                {'error': 'Invalid email or password'},
                'Invalid email or password',
                status.HTTP_401_UNAUTHORIZED,
            )

        user = authenticate(username=user_obj.username, password=password)   # proper hash check
        if user is None:
            return error_response(
                {'error': 'Invalid email or password'},
                'Invalid email or password',
                status.HTTP_401_UNAUTHORIZED,
            )

        refresh = RefreshToken.for_user(user)

        return success_response({
            'refresh' : str(refresh),
            'access' : str(refresh.access_token)
        }, 'Login successful')


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return success_response(response.data, 'Token refreshed successfully', response.status_code)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_api(request):
    reftesh_token = request.data.get('refresh')
    if not reftesh_token:
        return error_response(message="Refresh token is required", status_code=400)

    try:
        token = RefreshToken(reftesh_token)
        token.blacklist()
    except TokenError:
        return error_response(message="Invalid or expired token", status_code=400)

    return success_response(message="Logged out successfully")




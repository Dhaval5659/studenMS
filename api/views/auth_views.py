from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenRefreshView
from ..models import User
from ..serializers import registerSerializer
from ..utils import error_response, success_response
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from django.core.mail import send_mail
from django.conf import settings
from ..models import PasswordResetOTP
from ..throttles import ForgotPasswordThrottle, ResetPasswordThrottle


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
                {'message': 'Invalid email or password'},
                'Invalid email or password',
                status.HTTP_401_UNAUTHORIZED,
            )

        # --- Single session enforcement ---
        outstanding_tokens = OutstandingToken.objects.filter(user=user)
        for token in outstanding_tokens:
            BlacklistedToken.objects.get_or_create(token=token)
        # -----------------------------------

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
    refresh_token = request.data.get('refresh')
    if not refresh_token:
        return error_response(message="Refresh token is required", status_code=400)

    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
    except TokenError:
        return error_response(message="Invalid or expired token", status_code=400)

    return success_response(message="Logged out successfully")


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([ForgotPasswordThrottle])
def forgot_password_api(request):
    email = request.data.get('email')
    if not email:
        return error_response(message="Email is required", status_code=400)

    try:
        user = User.objects.get(email=email)
    except: 
        # Deliberately vague — don't reveal whether an email exists in your system
        return success_response(message="If this email is registered, an OTP has been sent")

    otp = PasswordResetOTP.generate_otp()
    PasswordResetOTP.objects.create(user=user, otp=otp)

    send_mail(
        subject='Your Password Reset OTP',
        message=f'Your OTP for password reset is: {otp}. It expires in 10 minutes.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )    

    return success_response(message="If this email is registered, an OTP has been sent")

@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([ResetPasswordThrottle])
def reset_password_api(request):
    email = request.data.get('email')
    otp = request.data.get('otp')
    new_password = request.data.get('new_password')

    if not email or not otp or not new_password:
        return error_response(message="Email, OTP and new password are all required", status_code=400)

    try: 
        user = User.objects.get(email=email)
    except:
        return error_response(message="Invalid or expired OTP", status_code=400)

    otp_obj = PasswordResetOTP.objects.filter(user=user, otp=otp).order_by('-created_at').first()

    user.set_password(new_password)
    user.save()

    otp_obj.is_used = True
    otp_obj.save()

    return success_response(message="Password reset successful")




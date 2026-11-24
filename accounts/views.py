from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserDetailSerializer


class RegisterView(APIView):
    """
    POST /api/auth/register/
    Register a new user with name, email, and password.
    Protected by rate throttling to prevent automated spam/bots.
    """
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'auth'
    serializer_class = UserRegistrationSerializer

    @extend_schema(
        request=UserRegistrationSerializer,
        responses={
            201: OpenApiResponse(description="User successfully registered"),
            400: OpenApiResponse(description="Validation error")
        },
        summary="Register a new user",
        description="Creates a new user record with name, email, and password."
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    'success': True,
                    'message': 'User registered successfully.',
                    'user': {
                        'id': user.id,
                        'name': user.name,
                        'email': user.email
                    },
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'tokens': {
                        'access': str(refresh.access_token),
                        'refresh': str(refresh)
                    }
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            {
                'success': False,
                'message': 'Validation failed.',
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class LoginView(APIView):
    """
    POST /api/auth/login/
    Log in a user and return a JWT token.
    Protected by rate throttling to defend against brute-force attacks.
    """
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'auth'
    serializer_class = UserLoginSerializer

    @extend_schema(
        request=UserLoginSerializer,
        responses={
            200: OpenApiResponse(description="Authentication successful"),
            400: OpenApiResponse(description="Invalid credentials or bad request")
        },
        summary="User login",
        description="Authenticates user with email and password, returning JWT access and refresh tokens."
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            user = validated_data['user']
            access_token = validated_data['access']
            refresh_token = validated_data['refresh']

            return Response(
                {
                    'success': True,
                    'message': 'Login successful.',
                    'user': {
                        'id': user.id,
                        'name': user.name,
                        'email': user.email
                    },
                    'access': access_token,
                    'refresh': refresh_token,
                    'tokens': {
                        'access': access_token,
                        'refresh': refresh_token
                    }
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {
                'success': False,
                'message': 'Login failed.',
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class CurrentUserView(APIView):
    """
    GET /api/auth/me/
    Retrieve current authenticated user details.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: UserDetailSerializer},
        summary="Current user profile",
        description="Returns profile of the currently authenticated user."
    )
    def get(self, request):
        serializer = UserDetailSerializer(request.user)
        return Response(
            {
                'success': True,
                'user': serializer.data
            },
            status=status.HTTP_200_OK
        )

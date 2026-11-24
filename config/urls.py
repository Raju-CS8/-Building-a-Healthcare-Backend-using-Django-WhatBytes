"""
URL configuration for healthcare backend project.
"""
from django.contrib import admin
from django.urls import path, include
from django.db import connection
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView
)


class HealthCheckView(APIView):
    """
    Health check endpoint verifying API uptime and PostgreSQL connectivity.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        db_status = 'connected'
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1;")
                cursor.fetchone()
        except Exception as e:
            db_status = f'error: {str(e)}'

        return Response({
            'status': 'healthy' if db_status == 'connected' else 'degraded',
            'database': db_status,
            'timestamp': timezone.now().isoformat(),
            'version': '1.0.0'
        })


class ApiRootView(APIView):
    """
    Healthcare Management System API Root
    """
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            'message': 'Welcome to the Healthcare Management System API',
            'version': '1.0.0',
            'status': 'healthy',
            'documentation': {
                'swagger': request.build_absolute_uri('/api/docs/'),
                'redoc': request.build_absolute_uri('/api/redoc/'),
                'schema': request.build_absolute_uri('/api/schema/'),
            },
            'health': request.build_absolute_uri('/api/health/'),
            'endpoints': {
                'auth': {
                    'register': request.build_absolute_uri('/api/auth/register/'),
                    'login': request.build_absolute_uri('/api/auth/login/'),
                    'me': request.build_absolute_uri('/api/auth/me/'),
                },
                'patients': request.build_absolute_uri('/api/patients/'),
                'doctors': request.build_absolute_uri('/api/doctors/'),
                'mappings': request.build_absolute_uri('/api/mappings/'),
            }
        })


urlpatterns = [
    path('admin/', admin.site.urls),

    # Health Check
    path('api/health/', HealthCheckView.as_view(), name='health-check'),

    # API Root
    path('', ApiRootView.as_view(), name='api-root-index'),
    path('api/', ApiRootView.as_view(), name='api-root'),

    # Application Endpoints
    path('api/auth/', include('accounts.urls', namespace='accounts')),
    path('api/patients/', include('patients.urls', namespace='patients')),
    path('api/doctors/', include('doctors.urls', namespace='doctors')),
    path('api/mappings/', include('mappings.urls', namespace='mappings')),

    # API Documentation (OpenAPI / Swagger / Redoc)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

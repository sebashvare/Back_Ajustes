from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .frontend_views import RegistroAjusteViewSet, UserViewSet
from . import auth_views

# Router para las APIs del frontend
frontend_router = DefaultRouter()
frontend_router.register(r'registros', RegistroAjusteViewSet, basename='registros')
frontend_router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    # URLs de autenticación compatibles con el frontend
    path('auth/login', auth_views.login, name='frontend_login'),
    path('auth/logout', auth_views.logout, name='frontend_logout'),
    path('auth/profile', auth_views.profile, name='frontend_profile'),
    path('auth/register', auth_views.register, name='frontend_register'),
    
    # URLs de la API compatible con el frontend
    path('api/', include(frontend_router.urls)),
]
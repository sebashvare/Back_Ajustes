from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.utils import timezone
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import UserProfile, SessionLog
from .serializers import (
    UserSerializer, RegisterSerializer, LoginSerializer,
    ChangePasswordSerializer, ProfileUpdateSerializer,
    SessionLogSerializer
)

def get_client_ip(request):
    """Obtener IP del cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

class CustomTokenObtainPairView(TokenObtainPairView):
    """Vista personalizada para obtener tokens JWT"""
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # Registrar sesión
            username = request.data.get('username')
            user = User.objects.get(username=username)
            
            SessionLog.objects.create(
                user=user,
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
        
        return response

class RegisterView(APIView):
    """Vista para registro de usuarios"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generar tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': 'Usuario registrado exitosamente',
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfileView(APIView):
    """Vista para ver y actualizar perfil del usuario"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        serializer = ProfileUpdateSerializer(
            request.user, 
            data=request.data, 
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(APIView):
    """Vista para cambiar contraseña"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            return Response({
                'message': 'Contraseña cambiada exitosamente'
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de usuarios (solo admin)"""
    queryset = User.objects.select_related('profile').all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Activar/desactivar usuario"""
        user = self.get_object()
        user.is_active = not user.is_active
        user.save()
        
        return Response({
            'message': f'Usuario {"activado" if user.is_active else "desactivado"} exitosamente',
            'is_active': user.is_active
        })
    
    @action(detail=True, methods=['post'])
    def set_permissions(self, request, pk=None):
        """Establecer permisos especiales del usuario"""
        user = self.get_object()
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        puede_aprobar = request.data.get('puede_aprobar_ajustes', False)
        puede_procesar = request.data.get('puede_procesar_ajustes', False)
        limite_aprobacion = request.data.get('limite_aprobacion')
        
        profile.puede_aprobar_ajustes = puede_aprobar
        profile.puede_procesar_ajustes = puede_procesar
        
        if limite_aprobacion is not None:
            profile.limite_aprobacion = limite_aprobacion
        
        profile.save()
        
        return Response({
            'message': 'Permisos actualizados exitosamente',
            'permissions': {
                'puede_aprobar_ajustes': profile.puede_aprobar_ajustes,
                'puede_procesar_ajustes': profile.puede_procesar_ajustes,
                'limite_aprobacion': profile.limite_aprobacion
            }
        })
    
    @action(detail=True, methods=['get'])
    def session_history(self, request, pk=None):
        """Obtener historial de sesiones del usuario"""
        user = self.get_object()
        sessions = SessionLog.objects.filter(user=user)[:20]  # Últimas 20 sesiones
        serializer = SessionLogSerializer(sessions, many=True)
        return Response(serializer.data)

class LogoutView(APIView):
    """Vista para logout"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        # Marcar sesión como inactiva
        try:
            session_log = SessionLog.objects.filter(
                user=request.user,
                is_active=True
            ).latest('login_time')
            
            session_log.logout_time = timezone.now()
            session_log.is_active = False
            session_log.save()
        except SessionLog.DoesNotExist:
            pass
        
        # Invalidar refresh token si se proporciona
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                pass
        
        return Response({
            'message': 'Logout exitoso'
        })

class SessionsView(APIView):
    """Vista para ver sesiones activas del usuario"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        sessions = SessionLog.objects.filter(
            user=request.user,
            is_active=True
        ).order_by('-login_time')
        
        serializer = SessionLogSerializer(sessions, many=True)
        return Response(serializer.data)
    
    def delete(self, request):
        """Cerrar todas las sesiones del usuario"""
        SessionLog.objects.filter(
            user=request.user,
            is_active=True
        ).update(
            logout_time=timezone.now(),
            is_active=False
        )
        
        return Response({
            'message': 'Todas las sesiones han sido cerradas'
        })

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from adjustments.frontend_serializers import UserSimpleSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """Endpoint de login compatible con el frontend Svelte"""
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not email or not password:
        return Response({
            'error': 'Email y contraseña son requeridos'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Buscar usuario por email
    try:
        user = User.objects.get(email=email)
        username = user.username
    except User.DoesNotExist:
        return Response({
            'error': 'Credenciales inválidas'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    # Autenticar usuario
    user = authenticate(username=username, password=password)
    if user:
        # Generar tokens JWT
        refresh = RefreshToken.for_user(user)
        user_serializer = UserSimpleSerializer(user)
        
        return Response({
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'user': user_serializer.data
        })
    else:
        return Response({
            'error': 'Credenciales inválidas'
        }, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """Endpoint de logout"""
    try:
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        return Response({'message': 'Logout exitoso'})
    except Exception as e:
        return Response({'error': 'Error en logout'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    """Obtener perfil del usuario actual"""
    serializer = UserSimpleSerializer(request.user)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Registro de nuevos usuarios"""
    email = request.data.get('email')
    password = request.data.get('password')
    name = request.data.get('name', '')
    
    if not email or not password:
        return Response({
            'error': 'Email y contraseña son requeridos'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Verificar si el usuario ya existe
    if User.objects.filter(email=email).exists():
        return Response({
            'error': 'El usuario ya existe'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Crear usuario
    user = User.objects.create_user(
        username=email,  # Usar email como username
        email=email,
        password=password,
        first_name=name.split(' ')[0] if name else '',
        last_name=' '.join(name.split(' ')[1:]) if len(name.split(' ')) > 1 else ''
    )
    
    # Generar tokens
    refresh = RefreshToken.for_user(user)
    user_serializer = UserSimpleSerializer(user)
    
    return Response({
        'access_token': str(refresh.access_token),
        'refresh_token': str(refresh),
        'user': user_serializer.data
    }, status=status.HTTP_201_CREATED)
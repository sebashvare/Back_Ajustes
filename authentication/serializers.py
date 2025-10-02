from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import UserProfile, SessionLog

class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer para UserProfile"""
    
    class Meta:
        model = UserProfile
        fields = [
            'telefono', 'documento_identidad', 'cargo', 'departamento',
            'recibir_notificaciones', 'tema_preferido', 'puede_aprobar_ajustes',
            'puede_procesar_ajustes', 'limite_aprobacion'
        ]
        read_only_fields = ['puede_aprobar_ajustes', 'puede_procesar_ajustes', 'limite_aprobacion']

class UserSerializer(serializers.ModelSerializer):
    """Serializer para User con perfil incluido"""
    profile = UserProfileSerializer(read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_active', 'date_joined', 'last_login', 'full_name', 'profile'
        ]
        read_only_fields = ['id', 'username', 'date_joined', 'last_login']
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username

class RegisterSerializer(serializers.ModelSerializer):
    """Serializer para registro de usuarios"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    # Campos del perfil
    telefono = serializers.CharField(required=False, allow_blank=True)
    documento_identidad = serializers.CharField(required=False, allow_blank=True)
    cargo = serializers.CharField(required=False, allow_blank=True)
    departamento = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'telefono', 'documento_identidad',
            'cargo', 'departamento'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Las contraseñas no coinciden.")
        return attrs
    
    def create(self, validated_data):
        # Extraer datos del perfil
        telefono = validated_data.pop('telefono', '')
        documento_identidad = validated_data.pop('documento_identidad', '')
        cargo = validated_data.pop('cargo', '')
        departamento = validated_data.pop('departamento', '')
        
        # Remover password_confirm
        validated_data.pop('password_confirm')
        
        # Crear usuario
        user = User.objects.create_user(**validated_data)
        
        # Crear perfil
        UserProfile.objects.create(
            user=user,
            telefono=telefono,
            documento_identidad=documento_identidad,
            cargo=cargo,
            departamento=departamento
        )
        
        return user

class LoginSerializer(serializers.Serializer):
    """Serializer para login"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(
                request=self.context.get('request'),
                username=username,
                password=password
            )
            
            if not user:
                raise serializers.ValidationError('Credenciales inválidas.')
            
            if not user.is_active:
                raise serializers.ValidationError('Cuenta de usuario desactivada.')
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Debe incluir "username" y "password".')

class ChangePasswordSerializer(serializers.Serializer):
    """Serializer para cambio de contraseña"""
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("Las nuevas contraseñas no coinciden.")
        return attrs
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("La contraseña actual es incorrecta.")
        return value

class ProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualización de perfil completo"""
    profile = UserProfileSerializer()
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'profile']
    
    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        
        # Actualizar usuario
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Actualizar perfil
        profile, created = UserProfile.objects.get_or_create(user=instance)
        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()
        
        return instance

class SessionLogSerializer(serializers.ModelSerializer):
    """Serializer para SessionLog"""
    user = UserSerializer(read_only=True)
    duration = serializers.SerializerMethodField()
    
    class Meta:
        model = SessionLog
        fields = '__all__'
        read_only_fields = ['id', 'login_time']
    
    def get_duration(self, obj):
        if obj.logout_time:
            delta = obj.logout_time - obj.login_time
            return str(delta)
        return None
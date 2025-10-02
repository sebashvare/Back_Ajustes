from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

class UserProfile(models.Model):
    """Perfil extendido del usuario"""
    user = models.OneToOneField(
        'auth.User', 
        on_delete=models.CASCADE, 
        related_name='profile'
    )
    
    # Información adicional
    telefono = models.CharField(
        max_length=15, 
        blank=True,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="El número de teléfono debe estar en formato: '+999999999'. Máximo 15 dígitos."
        )]
    )
    documento_identidad = models.CharField(max_length=20, blank=True)
    cargo = models.CharField(max_length=100, blank=True)
    departamento = models.CharField(max_length=100, blank=True)
    
    # Configuración de la aplicación
    recibir_notificaciones = models.BooleanField(default=True)
    tema_preferido = models.CharField(
        max_length=10,
        choices=[('light', 'Claro'), ('dark', 'Oscuro')],
        default='light'
    )
    
    # Información de permisos específicos
    puede_aprobar_ajustes = models.BooleanField(
        default=False,
        help_text="Puede aprobar ajustes financieros"
    )
    puede_procesar_ajustes = models.BooleanField(
        default=False,
        help_text="Puede procesar ajustes aprobados"
    )
    limite_aprobacion = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Límite de monto para aprobación"
    )
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuarios"
    
    def __str__(self):
        return f"Perfil de {self.user.get_full_name() or self.user.username}"
    
    @property
    def nombre_completo(self):
        return f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username

class SessionLog(models.Model):
    """Log de sesiones de usuarios"""
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='session_logs')
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Log de Sesión"
        verbose_name_plural = "Logs de Sesiones"
        ordering = ['-login_time']
    
    def __str__(self):
        return f"{self.user.username} - {self.login_time}"

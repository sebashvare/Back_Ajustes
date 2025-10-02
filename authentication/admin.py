from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, SessionLog

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Perfil'
    fields = [
        'telefono', 'documento_identidad', 'cargo', 'departamento',
        'recibir_notificaciones', 'tema_preferido', 
        'puede_aprobar_ajustes', 'puede_procesar_ajustes', 'limite_aprobacion'
    ]

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = BaseUserAdmin.list_display + ('get_cargo', 'get_departamento')
    
    def get_cargo(self, obj):
        try:
            return obj.profile.cargo
        except UserProfile.DoesNotExist:
            return '-'
    get_cargo.short_description = 'Cargo'
    
    def get_departamento(self, obj):
        try:
            return obj.profile.departamento
        except UserProfile.DoesNotExist:
            return '-'
    get_departamento.short_description = 'Departamento'

# Re-registrar el modelo User con el admin personalizado
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'cargo', 'departamento', 'puede_aprobar_ajustes', 
        'puede_procesar_ajustes', 'created_at'
    ]
    list_filter = [
        'puede_aprobar_ajustes', 'puede_procesar_ajustes', 
        'recibir_notificaciones', 'tema_preferido', 'created_at'
    ]
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'cargo', 'departamento']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['user__username']

@admin.register(SessionLog)
class SessionLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'ip_address', 'login_time', 'logout_time', 'is_active']
    list_filter = ['is_active', 'login_time']
    search_fields = ['user__username', 'ip_address']
    readonly_fields = ['login_time', 'logout_time']
    ordering = ['-login_time']
    
    def has_add_permission(self, request):
        return False  # No permitir crear sesiones manualmente

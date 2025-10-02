from django.contrib import admin
from .models import DashboardMetric, ReportTemplate, ReportExecution, UserActivity

@admin.register(DashboardMetric)
class DashboardMetricAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'valor', 'unidad', 'tipo_metrica', 'fecha_calculo', 'activo']
    list_filter = ['tipo_metrica', 'activo', 'fecha_calculo']
    search_fields = ['nombre', 'descripcion']
    readonly_fields = ['fecha_calculo']
    ordering = ['nombre']

@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo_reporte', 'formato_default', 'usuario_creador', 'es_publico', 'activo']
    list_filter = ['tipo_reporte', 'formato_default', 'es_publico', 'activo', 'created_at']
    search_fields = ['nombre', 'descripcion']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['nombre']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'descripcion', 'tipo_reporte')
        }),
        ('Configuración', {
            'fields': ('campos_incluidos', 'filtros_default', 'agrupacion', 'ordenamiento')
        }),
        ('Formato', {
            'fields': ('formato_default',)
        }),
        ('Permisos', {
            'fields': ('usuario_creador', 'es_publico', 'activo')
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(ReportExecution)
class ReportExecutionAdmin(admin.ModelAdmin):
    list_display = [
        'plantilla', 'usuario', 'formato', 'estado', 
        'registros_procesados', 'fecha_solicitud'
    ]
    list_filter = ['estado', 'formato', 'fecha_solicitud']
    search_fields = ['plantilla__nombre', 'usuario__username']
    readonly_fields = [
        'fecha_solicitud', 'fecha_inicio', 'fecha_fin', 
        'tiempo_ejecucion', 'registros_procesados'
    ]
    ordering = ['-fecha_solicitud']
    
    def has_add_permission(self, request):
        return False  # Las ejecuciones se crean automáticamente

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'accion', 'recurso', 'recurso_id', 'timestamp']
    list_filter = ['accion', 'recurso', 'timestamp']
    search_fields = ['usuario__username', 'accion', 'recurso', 'descripcion']
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']
    
    def has_add_permission(self, request):
        return False  # Las actividades se registran automáticamente
    
    def has_change_permission(self, request, obj=None):
        return False  # No permitir modificar actividades

from django.contrib import admin
from .models import (
    TipoAjuste, CuentaContable, AjusteFinanciero,
    HistorialAjuste, ArchivoAdjunto, ComentarioAjuste
)

@admin.register(TipoAjuste)
class TipoAjusteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion', 'activo', 'created_at']
    list_filter = ['activo', 'created_at']
    search_fields = ['nombre', 'descripcion']
    ordering = ['nombre']

@admin.register(CuentaContable)
class CuentaContableAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'tipo_cuenta', 'activo', 'created_at']
    list_filter = ['tipo_cuenta', 'activo', 'created_at']
    search_fields = ['codigo', 'nombre', 'descripcion']
    ordering = ['codigo']

@admin.register(AjusteFinanciero)
class AjusteFinancieroAdmin(admin.ModelAdmin):
    list_display = [
        'numero_ajuste', 'fecha_ajuste', 'concepto', 'monto', 
        'estado', 'prioridad', 'usuario_creador'
    ]
    list_filter = [
        'estado', 'prioridad', 'tipo_ajuste', 'moneda', 
        'fecha_ajuste', 'created_at'
    ]
    search_fields = [
        'numero_ajuste', 'concepto', 'descripcion', 
        'numero_documento_origen', 'referencia_externa'
    ]
    readonly_fields = [
        'numero_ajuste', 'created_at', 'updated_at',
        'fecha_aprobacion', 'fecha_procesamiento'
    ]
    date_hierarchy = 'fecha_ajuste'
    ordering = ['-fecha_ajuste']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('numero_ajuste', 'fecha_ajuste', 'fecha_valor')
        }),
        ('Clasificación', {
            'fields': ('tipo_ajuste', 'cuenta_debito', 'cuenta_credito')
        }),
        ('Montos', {
            'fields': ('monto', 'moneda')
        }),
        ('Descripción', {
            'fields': ('concepto', 'descripcion', 'justificacion', 'observaciones')
        }),
        ('Estado y Seguimiento', {
            'fields': ('estado', 'prioridad', 'fecha_vencimiento')
        }),
        ('Usuarios', {
            'fields': ('usuario_creador', 'usuario_aprobador', 'usuario_procesador')
        }),
        ('Fechas de Seguimiento', {
            'fields': ('fecha_aprobacion', 'fecha_procesamiento')
        }),
        ('Información Adicional', {
            'fields': ('numero_documento_origen', 'referencia_externa', 'centro_costo')
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(HistorialAjuste)
class HistorialAjusteAdmin(admin.ModelAdmin):
    list_display = ['ajuste', 'estado_anterior', 'estado_nuevo', 'usuario', 'fecha_cambio']
    list_filter = ['estado_anterior', 'estado_nuevo', 'fecha_cambio']
    search_fields = ['ajuste__numero_ajuste', 'comentario']
    readonly_fields = ['fecha_cambio']
    ordering = ['-fecha_cambio']

@admin.register(ArchivoAdjunto)
class ArchivoAdjuntoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'ajuste', 'usuario_subida', 'tamaño', 'fecha_subida']
    list_filter = ['tipo_contenido', 'fecha_subida']
    search_fields = ['nombre', 'descripcion', 'ajuste__numero_ajuste']
    readonly_fields = ['tamaño', 'tipo_contenido', 'fecha_subida']
    ordering = ['-fecha_subida']

@admin.register(ComentarioAjuste)
class ComentarioAjusteAdmin(admin.ModelAdmin):
    list_display = ['ajuste', 'usuario', 'es_interno', 'fecha_comentario']
    list_filter = ['es_interno', 'fecha_comentario']
    search_fields = ['ajuste__numero_ajuste', 'comentario']
    readonly_fields = ['fecha_comentario']
    ordering = ['-fecha_comentario']

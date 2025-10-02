from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta

class DashboardMetric(models.Model):
    """Métricas del dashboard"""
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    valor = models.DecimalField(max_digits=15, decimal_places=2)
    unidad = models.CharField(max_length=10, default='')
    tipo_metrica = models.CharField(max_length=20, choices=[
        ('CANTIDAD', 'Cantidad'),
        ('MONTO', 'Monto'),
        ('PORCENTAJE', 'Porcentaje'),
        ('TIEMPO', 'Tiempo'),
    ])
    fecha_calculo = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Métrica del Dashboard"
        verbose_name_plural = "Métricas del Dashboard"
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre}: {self.valor} {self.unidad}"

class ReportTemplate(models.Model):
    """Plantillas de reportes"""
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    tipo_reporte = models.CharField(max_length=20, choices=[
        ('RESUMEN', 'Resumen'),
        ('DETALLADO', 'Detallado'),
        ('ANALITICO', 'Analítico'),
        ('COMPARATIVO', 'Comparativo'),
    ])
    
    # Configuración del reporte
    campos_incluidos = models.JSONField(
        default=list,
        help_text="Lista de campos a incluir en el reporte"
    )
    filtros_default = models.JSONField(
        default=dict,
        help_text="Filtros por defecto para el reporte"
    )
    agrupacion = models.CharField(
        max_length=50,
        blank=True,
        help_text="Campo por el cual agrupar los datos"
    )
    ordenamiento = models.CharField(
        max_length=50,
        default='-fecha_ajuste',
        help_text="Campo para ordenar los resultados"
    )
    
    # Formato de salida
    formato_default = models.CharField(max_length=10, choices=[
        ('PDF', 'PDF'),
        ('EXCEL', 'Excel'),
        ('CSV', 'CSV'),
    ], default='PDF')
    
    # Metadatos
    usuario_creador = models.ForeignKey(User, on_delete=models.PROTECT)
    es_publico = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Plantilla de Reporte"
        verbose_name_plural = "Plantillas de Reportes"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre

class ReportExecution(models.Model):
    """Ejecuciones de reportes"""
    plantilla = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, related_name='ejecuciones')
    usuario = models.ForeignKey(User, on_delete=models.PROTECT)
    
    # Parámetros de ejecución
    parametros = models.JSONField(
        default=dict,
        help_text="Parámetros utilizados para generar el reporte"
    )
    formato = models.CharField(max_length=10, choices=[
        ('PDF', 'PDF'),
        ('EXCEL', 'Excel'),
        ('CSV', 'CSV'),
    ])
    
    # Estado de la ejecución
    estado = models.CharField(max_length=20, choices=[
        ('PENDIENTE', 'Pendiente'),
        ('PROCESANDO', 'Procesando'),
        ('COMPLETADO', 'Completado'),
        ('ERROR', 'Error'),
    ], default='PENDIENTE')
    
    # Resultados
    archivo_resultado = models.FileField(upload_to='reportes/%Y/%m/', null=True, blank=True)
    registros_procesados = models.PositiveIntegerField(default=0)
    tiempo_ejecucion = models.DurationField(null=True, blank=True)
    mensaje_error = models.TextField(blank=True)
    
    # Metadatos
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Ejecución de Reporte"
        verbose_name_plural = "Ejecuciones de Reportes"
        ordering = ['-fecha_solicitud']
    
    def __str__(self):
        return f"{self.plantilla.nombre} - {self.fecha_solicitud}"
    
    def marcar_inicio(self):
        """Marcar inicio de procesamiento"""
        self.estado = 'PROCESANDO'
        self.fecha_inicio = timezone.now()
        self.save(update_fields=['estado', 'fecha_inicio'])
    
    def marcar_completado(self, archivo_path=None, registros=0):
        """Marcar como completado"""
        self.estado = 'COMPLETADO'
        self.fecha_fin = timezone.now()
        self.registros_procesados = registros
        
        if self.fecha_inicio:
            self.tiempo_ejecucion = self.fecha_fin - self.fecha_inicio
        
        if archivo_path:
            self.archivo_resultado = archivo_path
        
        self.save()
    
    def marcar_error(self, mensaje_error):
        """Marcar como error"""
        self.estado = 'ERROR'
        self.fecha_fin = timezone.now()
        self.mensaje_error = mensaje_error
        
        if self.fecha_inicio:
            self.tiempo_ejecucion = self.fecha_fin - self.fecha_inicio
        
        self.save()

class UserActivity(models.Model):
    """Registro de actividades de usuarios"""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='actividades')
    accion = models.CharField(max_length=50)
    recurso = models.CharField(max_length=100)  # ej: "ajuste_financiero", "reporte"
    recurso_id = models.CharField(max_length=50, blank=True)  # ID del recurso afectado
    descripcion = models.TextField(blank=True)
    
    # Metadatos de la sesión
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    
    # Timestamps
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Actividad de Usuario"
        verbose_name_plural = "Actividades de Usuarios"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['usuario', 'timestamp']),
            models.Index(fields=['accion']),
            models.Index(fields=['recurso']),
        ]
    
    def __str__(self):
        return f"{self.usuario.username} - {self.accion} - {self.timestamp}"

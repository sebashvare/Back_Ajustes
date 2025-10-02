from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

# Importar el nuevo modelo compatible con el frontend
from .frontend_models import RegistroAjuste

class TipoAjuste(models.Model):
    """Tipos de ajustes financieros disponibles"""
    TIPO_CHOICES = [
        ('DEBITO', 'Débito'),
        ('CREDITO', 'Crédito'),
        ('TRANSFERENCIA', 'Transferencia'),
        ('REVERSO', 'Reverso'),
        ('CORRECCION', 'Corrección'),
    ]
    
    nombre = models.CharField(max_length=50, choices=TIPO_CHOICES, unique=True)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Tipo de Ajuste"
        verbose_name_plural = "Tipos de Ajustes"
        ordering = ['nombre']
    
    def __str__(self):
        return self.get_nombre_display()

class CuentaContable(models.Model):
    """Cuentas contables para los ajustes"""
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    tipo_cuenta = models.CharField(max_length=20, choices=[
        ('ACTIVO', 'Activo'),
        ('PASIVO', 'Pasivo'),
        ('PATRIMONIO', 'Patrimonio'),
        ('INGRESO', 'Ingreso'),
        ('GASTO', 'Gasto'),
    ])
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Cuenta Contable"
        verbose_name_plural = "Cuentas Contables"
        ordering = ['codigo']
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

class AjusteFinanciero(models.Model):
    """Modelo principal para registrar ajustes financieros"""
    ESTADO_CHOICES = [
        ('BORRADOR', 'Borrador'),
        ('PENDIENTE', 'Pendiente'),
        ('APROBADO', 'Aprobado'),
        ('RECHAZADO', 'Rechazado'),
        ('PROCESADO', 'Procesado'),
        ('ANULADO', 'Anulado'),
    ]
    
    PRIORIDAD_CHOICES = [
        ('BAJA', 'Baja'),
        ('MEDIA', 'Media'),
        ('ALTA', 'Alta'),
        ('URGENTE', 'Urgente'),
    ]
    
    # Información básica
    numero_ajuste = models.CharField(max_length=20, unique=True, editable=False)
    fecha_ajuste = models.DateTimeField()
    fecha_valor = models.DateField()
    
    # Clasificación
    tipo_ajuste = models.ForeignKey(TipoAjuste, on_delete=models.PROTECT)
    cuenta_debito = models.ForeignKey(
        CuentaContable, 
        on_delete=models.PROTECT, 
        related_name='ajustes_debito'
    )
    cuenta_credito = models.ForeignKey(
        CuentaContable, 
        on_delete=models.PROTECT, 
        related_name='ajustes_credito'
    )
    
    # Montos
    monto = models.DecimalField(
        max_digits=15, 
        decimal_places=2,
        validators=[
            MaxValueValidator(Decimal('-0.01'), message="El valor del ajuste debe ser negativo"),
            MinValueValidator(Decimal('-999999999999.99'), message="El valor excede el límite mínimo permitido")
        ]
    )
    moneda = models.CharField(max_length=3, default='COP')
    
    # Descripciones y justificación
    concepto = models.CharField(max_length=200)
    descripcion = models.TextField()
    justificacion = models.TextField()
    observaciones = models.TextField(blank=True)
    
    # Estado y seguimiento
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='BORRADOR')
    prioridad = models.CharField(max_length=10, choices=PRIORIDAD_CHOICES, default='MEDIA')
    
    # Usuarios involucrados
    usuario_creador = models.ForeignKey(
        User, 
        on_delete=models.PROTECT, 
        related_name='ajustes_creados'
    )
    usuario_aprobador = models.ForeignKey(
        User, 
        on_delete=models.PROTECT, 
        related_name='ajustes_aprobados',
        null=True, 
        blank=True
    )
    usuario_procesador = models.ForeignKey(
        User, 
        on_delete=models.PROTECT, 
        related_name='ajustes_procesados',
        null=True, 
        blank=True
    )
    
    # Fechas de seguimiento
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    fecha_procesamiento = models.DateTimeField(null=True, blank=True)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Campos adicionales para trazabilidad
    numero_documento_origen = models.CharField(max_length=50, blank=True)
    referencia_externa = models.CharField(max_length=100, blank=True)
    centro_costo = models.CharField(max_length=50, blank=True)
    
    class Meta:
        verbose_name = "Ajuste Financiero"
        verbose_name_plural = "Ajustes Financieros"
        ordering = ['-fecha_ajuste', '-numero_ajuste']
        indexes = [
            models.Index(fields=['numero_ajuste']),
            models.Index(fields=['fecha_ajuste']),
            models.Index(fields=['estado']),
            models.Index(fields=['tipo_ajuste']),
            models.Index(fields=['usuario_creador']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.numero_ajuste:
            # Generar número de ajuste automáticamente
            ultimo_numero = AjusteFinanciero.objects.count() + 1
            self.numero_ajuste = f"AJ{ultimo_numero:08d}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.numero_ajuste} - {self.concepto}"
    
    @property
    def puede_ser_editado(self):
        return self.estado in ['BORRADOR', 'RECHAZADO']
    
    @property
    def puede_ser_aprobado(self):
        return self.estado == 'PENDIENTE'
    
    @property
    def puede_ser_procesado(self):
        return self.estado == 'APROBADO'

class HistorialAjuste(models.Model):
    """Historial de cambios de estado de los ajustes"""
    ajuste = models.ForeignKey(AjusteFinanciero, on_delete=models.CASCADE, related_name='historial')
    estado_anterior = models.CharField(max_length=10, choices=AjusteFinanciero.ESTADO_CHOICES)
    estado_nuevo = models.CharField(max_length=10, choices=AjusteFinanciero.ESTADO_CHOICES)
    usuario = models.ForeignKey(User, on_delete=models.PROTECT)
    comentario = models.TextField(blank=True)
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Historial de Ajuste"
        verbose_name_plural = "Historiales de Ajustes"
        ordering = ['-fecha_cambio']
    
    def __str__(self):
        return f"{self.ajuste.numero_ajuste} - {self.estado_anterior} → {self.estado_nuevo}"

class ArchivoAdjunto(models.Model):
    """Archivos adjuntos a los ajustes"""
    ajuste = models.ForeignKey(AjusteFinanciero, on_delete=models.CASCADE, related_name='archivos')
    nombre = models.CharField(max_length=255)
    archivo = models.FileField(upload_to='ajustes/archivos/%Y/%m/')
    descripcion = models.TextField(blank=True)
    tamaño = models.PositiveIntegerField(help_text="Tamaño en bytes")
    tipo_contenido = models.CharField(max_length=100)
    usuario_subida = models.ForeignKey(User, on_delete=models.PROTECT)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Archivo Adjunto"
        verbose_name_plural = "Archivos Adjuntos"
        ordering = ['-fecha_subida']
    
    def __str__(self):
        return f"{self.nombre} - {self.ajuste.numero_ajuste}"

class ComentarioAjuste(models.Model):
    """Comentarios en los ajustes"""
    ajuste = models.ForeignKey(AjusteFinanciero, on_delete=models.CASCADE, related_name='comentarios')
    usuario = models.ForeignKey(User, on_delete=models.PROTECT)
    comentario = models.TextField()
    es_interno = models.BooleanField(default=False, help_text="Comentario visible solo para usuarios internos")
    fecha_comentario = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Comentario de Ajuste"
        verbose_name_plural = "Comentarios de Ajustes"
        ordering = ['-fecha_comentario']
    
    def __str__(self):
        return f"Comentario por {self.usuario.username} en {self.ajuste.numero_ajuste}"

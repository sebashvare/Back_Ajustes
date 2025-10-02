"""
=============================================================================
MODELOS DE DATOS - SISTEMA DE REGISTRO DE AJUSTES
=============================================================================

Modelos Django optimizados para compatibilidad con el frontend Svelte.
Incluye validaciones, índices y configuraciones para producción.

Autor: Sistema de Desarrollo
Versión: 1.0.0
Fecha: Octubre 2025
=============================================================================
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import date
import logging

# Configurar logging para este módulo
logger = logging.getLogger(__name__)


class RegistroAjuste(models.Model):
    """
    Modelo principal para registros de ajustes financieros.
    
    Este modelo está diseñado para ser compatible con la estructura de datos
    esperada por el frontend Svelte, manteniendo los nombres de campos
    exactos requeridos por la interfaz de usuario.
    
    Attributes:
        id_cuenta (str): Identificador único de la cuenta contable
        id_acuerdo_servicio (str): Identificador del acuerdo de servicio
        id_cargo_facturable (str): Identificador del cargo facturable
        fecha_ajuste (date): Fecha en la que se realiza el ajuste
        asesor_que_ajusto (str): Nombre del asesor responsable del ajuste
        valor_ajustado (Decimal): Monto del ajuste en valor monetario
        obs_adicional (str): Observaciones adicionales opcionales
        justificacion (str): Justificación requerida para el ajuste
        created_at (datetime): Timestamp de creación del registro
        updated_at (datetime): Timestamp de última actualización
        created_by (User): Usuario que creó el registro
    
    Business Rules:
        - El valor del ajuste no puede ser cero
        - La fecha del ajuste no puede ser futura
        - La justificación es obligatoria para todos los ajustes
        - Ajustes superiores a 100,000 requieren aprobación adicional
    """
    
    # ==========================================================================
    # CAMPOS PRINCIPALES DEL REGISTRO
    # ==========================================================================
    
    id_cuenta = models.CharField(
        max_length=50,
        verbose_name="ID de Cuenta",
        help_text="Identificador único de la cuenta contable",
        db_index=True  # Índice para búsquedas frecuentes
    )
    
    id_acuerdo_servicio = models.CharField(
        max_length=50,
        verbose_name="ID de Acuerdo de Servicio",
        help_text="Identificador del acuerdo de servicio asociado",
        db_index=True
    )
    
    id_cargo_facturable = models.CharField(
        max_length=50,
        verbose_name="ID de Cargo Facturable",
        help_text="Identificador del cargo facturable específico"
    )
    
    fecha_ajuste = models.DateField(
        verbose_name="Fecha de Ajuste",
        help_text="Fecha en la que se realiza el ajuste (no puede ser futura)",
        db_index=True
    )
    
    asesor_que_ajusto = models.CharField(
        max_length=100,
        verbose_name="Asesor que Ajustó",
        help_text="Nombre completo del asesor responsable del ajuste",
        db_index=True
    )
    
    # ==========================================================================
    # VALOR MONETARIO Y DESCRIPCIONES
    # ==========================================================================
    
    valor_ajustado = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Valor Ajustado",
        help_text="Monto del ajuste en pesos colombianos (no puede ser cero)",
        validators=[
            MinValueValidator(Decimal('0.01'), message="El valor debe ser mayor a cero"),
            MaxValueValidator(Decimal('999999999999.99'), message="El valor excede el límite permitido")
        ]
    )
    
    obs_adicional = models.TextField(
        blank=True,
        verbose_name="Observaciones Adicionales",
        help_text="Observaciones adicionales sobre el ajuste (opcional)",
        max_length=1000
    )
    
    justificacion = models.TextField(
        verbose_name="Justificación",
        help_text="Justificación detallada para el ajuste (obligatorio)",
        max_length=2000
    )
    
    # ==========================================================================
    # CAMPOS DE AUDITORÍA Y CONTROL
    # ==========================================================================
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación",
        help_text="Timestamp automático de creación del registro",
        db_index=True
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de Actualización",
        help_text="Timestamp automático de última actualización"
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,  # Proteger registros si se elimina el usuario
        related_name='registros_creados',
        verbose_name="Creado por",
        help_text="Usuario que creó este registro",
        null=True,
        blank=True
    )
    
    # ==========================================================================
    # METADATOS DEL MODELO
    # ==========================================================================
    
    class Meta:
        verbose_name = "Registro de Ajuste"
        verbose_name_plural = "Registros de Ajustes"
        ordering = ['-created_at']  # Más recientes primero
        
        # Índices para optimizar consultas frecuentes
        indexes = [
            models.Index(fields=['id_cuenta'], name='idx_cuenta'),
            models.Index(fields=['fecha_ajuste'], name='idx_fecha_ajuste'),
            models.Index(fields=['asesor_que_ajusto'], name='idx_asesor'),
            models.Index(fields=['created_at'], name='idx_created_at'),
            models.Index(fields=['valor_ajustado'], name='idx_valor'),
            # Índice compuesto para búsquedas por cuenta y fecha
            models.Index(fields=['id_cuenta', 'fecha_ajuste'], name='idx_cuenta_fecha'),
        ]
        
        # Permisos personalizados
        permissions = [
            ("view_high_value_adjustments", "Puede ver ajustes de alto valor"),
            ("approve_adjustments", "Puede aprobar ajustes"),
            ("export_adjustments", "Puede exportar ajustes"),
        ]
    
    # ==========================================================================
    # MÉTODOS DE INSTANCIA
    # ==========================================================================
    
    def __str__(self):
        """
        Representación en cadena del registro para admin y logging.
        
        Returns:
            str: Cadena descriptiva del registro
        """
        return f"{self.id_cuenta} - {self.fecha_ajuste} - ${self.valor_ajustado:,.2f}"
    
    def clean(self):
        """
        Validaciones personalizadas a nivel de modelo.
        
        Raises:
            ValidationError: Si alguna validación falla
        """
        errors = {}
        
        # Validar que la fecha no sea futura
        if self.fecha_ajuste and self.fecha_ajuste > date.today():
            errors['fecha_ajuste'] = "La fecha del ajuste no puede ser futura"
        
        # Validar que el valor no sea cero
        if self.valor_ajustado and self.valor_ajustado == 0:
            errors['valor_ajustado'] = "El valor del ajuste no puede ser cero"
        
        # Validar longitud mínima de justificación
        if self.justificacion and len(self.justificacion.strip()) < 10:
            errors['justificacion'] = "La justificación debe tener al menos 10 caracteres"
        
        if errors:
            raise ValidationError(errors)
    
    def save(self, *args, **kwargs):
        """
        Sobrescribir save para agregar validaciones y logging.
        
        Args:
            *args: Argumentos posicionales
            **kwargs: Argumentos nombrados
        """
        # Ejecutar validaciones personalizadas
        self.full_clean()
        
        # Logging para auditoría
        if self.pk:
            logger.info(f"Actualizando registro de ajuste ID: {self.pk}")
        else:
            logger.info(f"Creando nuevo registro de ajuste para cuenta: {self.id_cuenta}")
        
        # Llamar al save original
        super().save(*args, **kwargs)
    
    # ==========================================================================
    # PROPIEDADES CALCULADAS
    # ==========================================================================
    
    @property
    def valor_ajustado_display(self):
        """
        Formatear el valor ajustado para mostrar en interfaz.
        
        Returns:
            str: Valor formateado con símbolo de moneda
        """
        return f"${self.valor_ajustado:,.2f}"
    
    @property
    def es_ajuste_alto_valor(self):
        """
        Determinar si el ajuste requiere aprobación especial.
        
        Returns:
            bool: True si requiere aprobación especial
        """
        from django.conf import settings
        limite = getattr(settings, 'ADJUSTMENTS_SETTINGS', {}).get('REQUIRE_APPROVAL_ABOVE', 100000)
        return self.valor_ajustado >= limite
    
    @property
    def edad_registro(self):
        """
        Calcular la edad del registro en días.
        
        Returns:
            int: Número de días desde la creación
        """
        from django.utils import timezone
        return (timezone.now().date() - self.created_at.date()).days
    
    # ==========================================================================
    # MÉTODOS DE CLASE
    # ==========================================================================
    
    @classmethod
    def obtener_resumen_estadisticas(cls):
        """
        Obtener estadísticas resumidas de todos los registros.
        
        Returns:
            dict: Diccionario con estadísticas
        """
        from django.db.models import Sum, Avg, Count
        
        stats = cls.objects.aggregate(
            total_registros=Count('id'),
            suma_total=Sum('valor_ajustado'),
            promedio=Avg('valor_ajustado')
        )
        
        return {
            'total_registros': stats['total_registros'] or 0,
            'suma_total': stats['suma_total'] or Decimal('0.00'),
            'promedio': stats['promedio'] or Decimal('0.00'),
        }
    
    @classmethod
    def obtener_por_asesor(cls, asesor):
        """
        Obtener todos los registros de un asesor específico.
        
        Args:
            asesor (str): Nombre del asesor
            
        Returns:
            QuerySet: Registros del asesor ordenados por fecha
        """
        return cls.objects.filter(
            asesor_que_ajusto__icontains=asesor
        ).order_by('-fecha_ajuste')
        """Formatear el valor para mostrar"""
        return f"${self.valor_ajustado:,.2f}"
"""
=============================================================================
SERIALIZERS - SISTEMA DE REGISTRO DE AJUSTES
=============================================================================

Serializers Django REST Framework optimizados para la API del frontend Svelte.
Incluye validaciones, formateo de datos y optimizaciones de performance.

Autor: Sistema de Desarrollo
Versión: 1.0.0
Fecha: Octubre 2025
=============================================================================
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import date
import logging

# Importar modelos locales
from .frontend_models import RegistroAjuste

# Configurar logging para este módulo
logger = logging.getLogger(__name__)


class RegistroAjusteSerializer(serializers.ModelSerializer):
    """
    Serializer principal para el modelo RegistroAjuste.
    
    Este serializer está optimizado para ser compatible con la estructura
    de datos esperada por el frontend Svelte, incluyendo formateo de fechas
    y validaciones de negocio específicas.
    
    Features:
        - Validaciones personalizadas para reglas de negocio
        - Formateo automático de fechas en formato ISO
        - Campos de solo lectura para auditoría
        - Optimizaciones para consultas de la API
    """
    
    # Campos calculados para la respuesta
    valor_ajustado_display = serializers.SerializerMethodField()
    es_ajuste_alto_valor = serializers.SerializerMethodField()
    edad_registro = serializers.SerializerMethodField()
    
    class Meta:
        model = RegistroAjuste
        fields = [
            # Campos principales del registro
            'id',
            'id_cuenta',
            'id_acuerdo_servicio',
            'id_cargo_facturable',
            'fecha_ajuste',
            'asesor_que_ajusto',
            'valor_ajustado',
            'obs_adicional',
            'justificacion',
            
            # Campos de auditoría
            'created_at',
            'updated_at',
            
            # Campos calculados
            'valor_ajustado_display',
            'es_ajuste_alto_valor',
            'edad_registro',
        ]
        
        # Campos de solo lectura (no modificables por la API)
        read_only_fields = [
            'id', 
            'created_at', 
            'updated_at',
            'valor_ajustado_display',
            'es_ajuste_alto_valor',
            'edad_registro',
        ]
        
        # Configuración adicional para optimización
        extra_kwargs = {
            'valor_ajustado': {
                'min_value': Decimal('0.01'),
                'max_digits': 15,
                'decimal_places': 2,
            },
            'justificacion': {
                'min_length': 10,
                'max_length': 2000,
            },
            'obs_adicional': {
                'max_length': 1000,
                'allow_blank': True,
            },
        }
    
    def get_valor_ajustado_display(self, obj):
        """
        Formatear el valor ajustado para mostrar en la interfaz.
        
        Args:
            obj (RegistroAjuste): Instancia del modelo
            
        Returns:
            str: Valor formateado con símbolo de moneda
        """
        return obj.valor_ajustado_display
    
    def get_es_ajuste_alto_valor(self, obj):
        """
        Determinar si el ajuste requiere aprobación especial.
        
        Args:
            obj (RegistroAjuste): Instancia del modelo
            
        Returns:
            bool: True si requiere aprobación especial
        """
        return obj.es_ajuste_alto_valor
    
    def get_edad_registro(self, obj):
        """
        Calcular la edad del registro en días.
        
        Args:
            obj (RegistroAjuste): Instancia del modelo
            
        Returns:
            int: Número de días desde la creación
        """
        return obj.edad_registro
    
    def validate_fecha_ajuste(self, value):
        """
        Validar que la fecha de ajuste no sea futura.
        
        Args:
            value (date): Fecha a validar
            
        Returns:
            date: Fecha validada
            
        Raises:
            serializers.ValidationError: Si la fecha es futura
        """
        if value > date.today():
            raise serializers.ValidationError(
                "La fecha del ajuste no puede ser futura."
            )
        return value
    
    def validate_valor_ajustado(self, value):
        """
        Validar el valor del ajuste según reglas de negocio.
        
        Args:
            value (Decimal): Valor a validar
            
        Returns:
            Decimal: Valor validado
            
        Raises:
            serializers.ValidationError: Si el valor no cumple las reglas
        """
        if value <= 0:
            raise serializers.ValidationError(
                "El valor del ajuste debe ser mayor a cero."
            )
        
        # Validar límite máximo desde configuración
        from django.conf import settings
        max_value = getattr(settings, 'ADJUSTMENTS_SETTINGS', {}).get(
            'MAX_ADJUSTMENT_VALUE', 10000000
        )
        
        if value > max_value:
            raise serializers.ValidationError(
                f"El valor del ajuste no puede exceder ${max_value:,.2f}"
            )
        
        return value
    
    def validate_justificacion(self, value):
        """
        Validar la justificación del ajuste.
        
        Args:
            value (str): Justificación a validar
            
        Returns:
            str: Justificación validada
            
        Raises:
            serializers.ValidationError: Si la justificación no es válida
        """
        if not value or len(value.strip()) < 10:
            raise serializers.ValidationError(
                "La justificación debe tener al menos 10 caracteres."
            )
        
        # Validar palabras prohibidas o patrones no deseados
        palabras_prohibidas = ['test', 'prueba', 'xxxx', 'aaaa']
        if any(palabra in value.lower() for palabra in palabras_prohibidas):
            raise serializers.ValidationError(
                "La justificación no puede contener texto de prueba."
            )
        
        return value.strip()
    
    def validate(self, attrs):
        """
        Validaciones a nivel de objeto completo.
        
        Args:
            attrs (dict): Atributos del objeto
            
        Returns:
            dict: Atributos validados
            
        Raises:
            serializers.ValidationError: Si alguna validación falla
        """
        # Validar coherencia entre campos
        valor_ajustado = attrs.get('valor_ajustado')
        justificacion = attrs.get('justificacion', '')
        
        # Ajustes de alto valor requieren justificación más detallada
        if valor_ajustado and valor_ajustado >= 100000:
            if len(justificacion.strip()) < 50:
                raise serializers.ValidationError({
                    'justificacion': 'Ajustes de alto valor requieren justificación detallada (mínimo 50 caracteres).'
                })
        
        return attrs
    
    def to_representation(self, instance):
        """
        Personalizar la representación de salida para el frontend.
        
        Args:
            instance (RegistroAjuste): Instancia del modelo
            
        Returns:
            dict: Datos serializados personalizados
        """
        data = super().to_representation(instance)
        
        # Formatear fechas en formato ISO esperado por el frontend
        if data.get('fecha_ajuste'):
            data['fecha_ajuste'] = instance.fecha_ajuste.isoformat()
        
        # Formatear timestamps con zona horaria
        if data.get('created_at'):
            data['created_at'] = instance.created_at.isoformat()
        
        if data.get('updated_at'):
            data['updated_at'] = instance.updated_at.isoformat()
        
        # Agregar metadatos útiles para el frontend
        data['_metadata'] = {
            'version': '1.0.0',
            'last_updated': instance.updated_at.isoformat(),
            'requires_approval': instance.es_ajuste_alto_valor,
        }
        
        return data
    
    def create(self, validated_data):
        """
        Crear nueva instancia con logging de auditoría.
        
        Args:
            validated_data (dict): Datos validados
            
        Returns:
            RegistroAjuste: Instancia creada
        """
        # Obtener usuario del contexto de la request
        user = self.context.get('request').user if self.context.get('request') else None
        if user and user.is_authenticated:
            validated_data['created_by'] = user
        
        # Logging para auditoría
        logger.info(
            f"Creando nuevo registro de ajuste para cuenta: {validated_data.get('id_cuenta')} "
            f"por valor: ${validated_data.get('valor_ajustado')}"
        )
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """
        Actualizar instancia existente con logging de auditoría.
        
        Args:
            instance (RegistroAjuste): Instancia a actualizar
            validated_data (dict): Datos validados
            
        Returns:
            RegistroAjuste: Instancia actualizada
        """
        # Logging para auditoría
        logger.info(
            f"Actualizando registro ID: {instance.id} - "
            f"Cuenta: {instance.id_cuenta}"
        )
        
        return super().update(instance, validated_data)


class UserSimpleSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para usuarios según la estructura esperada por el frontend.
    
    Este serializer proporciona información básica del usuario en el formato
    exacto requerido por la interfaz Svelte.
    
    Features:
        - Campos mínimos necesarios para el frontend
        - Formateo de nombre completo
        - Determinación automática de roles
        - Optimizado para respuestas rápidas
    """
    
    # Campos calculados
    name = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'name',
            'role'
        ]
        
        # Solo campos de lectura para seguridad
        read_only_fields = ['id', 'email', 'name', 'role']
    
    def get_name(self, obj):
        """
        Obtener el nombre completo del usuario.
        
        Args:
            obj (User): Instancia del usuario
            
        Returns:
            str: Nombre completo o username si no hay nombre
        """
        if obj.first_name or obj.last_name:
            return f"{obj.first_name} {obj.last_name}".strip()
        return obj.username
    
    def get_role(self, obj):
        """
        Determinar el rol del usuario basado en permisos.
        
        Args:
            obj (User): Instancia del usuario
            
        Returns:
            str: Rol del usuario (admin, staff, user)
        """
        if obj.is_superuser:
            return 'admin'
        elif obj.is_staff:
            return 'staff'
        else:
            return 'user'


class EstadisticasSerializer(serializers.Serializer):
    """
    Serializer para estadísticas agregadas del sistema.
    
    Proporciona métricas resumidas para dashboards y reportes.
    """
    
    total_registros = serializers.IntegerField(
        help_text="Número total de registros en el sistema"
    )
    
    total_valor = serializers.DecimalField(
        max_digits=20,
        decimal_places=2,
        help_text="Suma total de todos los valores ajustados"
    )
    
    promedio_valor = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Promedio de valores ajustados"
    )
    
    registros_ultimo_mes = serializers.IntegerField(
        required=False,
        help_text="Registros creados en el último mes"
    )
    
    asesores_activos = serializers.IntegerField(
        required=False,
        help_text="Número de asesores que han realizado ajustes"
    )
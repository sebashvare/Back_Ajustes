from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    TipoAjuste, CuentaContable, AjusteFinanciero, 
    HistorialAjuste, ArchivoAdjunto, ComentarioAjuste
)

class UserSerializer(serializers.ModelSerializer):
    """Serializer básico para User"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'full_name']
        read_only_fields = ['id', 'username', 'email']
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username

class TipoAjusteSerializer(serializers.ModelSerializer):
    """Serializer para TipoAjuste"""
    display_name = serializers.CharField(source='get_nombre_display', read_only=True)
    
    class Meta:
        model = TipoAjuste
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class CuentaContableSerializer(serializers.ModelSerializer):
    """Serializer para CuentaContable"""
    
    class Meta:
        model = CuentaContable
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class HistorialAjusteSerializer(serializers.ModelSerializer):
    """Serializer para HistorialAjuste"""
    usuario = UserSerializer(read_only=True)
    estado_anterior_display = serializers.CharField(source='get_estado_anterior_display', read_only=True)
    estado_nuevo_display = serializers.CharField(source='get_estado_nuevo_display', read_only=True)
    
    class Meta:
        model = HistorialAjuste
        fields = '__all__'
        read_only_fields = ['id', 'fecha_cambio']

class ArchivoAdjuntoSerializer(serializers.ModelSerializer):
    """Serializer para ArchivoAdjunto"""
    usuario_subida = UserSerializer(read_only=True)
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = ArchivoAdjunto
        fields = '__all__'
        read_only_fields = ['id', 'usuario_subida', 'fecha_subida', 'tamaño', 'tipo_contenido']
    
    def get_url(self, obj):
        if obj.archivo:
            return obj.archivo.url
        return None
    
    def create(self, validated_data):
        # Obtener información del archivo
        archivo = validated_data['archivo']
        validated_data['tamaño'] = archivo.size
        validated_data['tipo_contenido'] = archivo.content_type
        validated_data['usuario_subida'] = self.context['request'].user
        return super().create(validated_data)

class ComentarioAjusteSerializer(serializers.ModelSerializer):
    """Serializer para ComentarioAjuste"""
    usuario = UserSerializer(read_only=True)
    
    class Meta:
        model = ComentarioAjuste
        fields = '__all__'
        read_only_fields = ['id', 'usuario', 'fecha_comentario']
    
    def create(self, validated_data):
        validated_data['usuario'] = self.context['request'].user
        return super().create(validated_data)

class AjusteFinancieroListSerializer(serializers.ModelSerializer):
    """Serializer para listar ajustes financieros (vista resumida)"""
    tipo_ajuste = TipoAjusteSerializer(read_only=True)
    usuario_creador = UserSerializer(read_only=True)
    usuario_aprobador = UserSerializer(read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    prioridad_display = serializers.CharField(source='get_prioridad_display', read_only=True)
    cuenta_debito_nombre = serializers.CharField(source='cuenta_debito.nombre', read_only=True)
    cuenta_credito_nombre = serializers.CharField(source='cuenta_credito.nombre', read_only=True)
    
    class Meta:
        model = AjusteFinanciero
        fields = [
            'id', 'numero_ajuste', 'fecha_ajuste', 'fecha_valor', 'tipo_ajuste',
            'monto', 'moneda', 'concepto', 'estado', 'estado_display', 
            'prioridad', 'prioridad_display', 'usuario_creador', 'usuario_aprobador',
            'cuenta_debito_nombre', 'cuenta_credito_nombre', 'created_at', 'updated_at'
        ]

class AjusteFinancieroDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para ajustes financieros"""
    tipo_ajuste = TipoAjusteSerializer(read_only=True)
    cuenta_debito = CuentaContableSerializer(read_only=True)
    cuenta_credito = CuentaContableSerializer(read_only=True)
    usuario_creador = UserSerializer(read_only=True)
    usuario_aprobador = UserSerializer(read_only=True)
    usuario_procesador = UserSerializer(read_only=True)
    
    # Campos calculados
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    prioridad_display = serializers.CharField(source='get_prioridad_display', read_only=True)
    puede_ser_editado = serializers.ReadOnlyField()
    puede_ser_aprobado = serializers.ReadOnlyField()
    puede_ser_procesado = serializers.ReadOnlyField()
    
    # Relaciones anidadas
    historial = HistorialAjusteSerializer(many=True, read_only=True)
    archivos = ArchivoAdjuntoSerializer(many=True, read_only=True)
    comentarios = ComentarioAjusteSerializer(many=True, read_only=True)
    
    class Meta:
        model = AjusteFinanciero
        fields = '__all__'
        read_only_fields = [
            'id', 'numero_ajuste', 'usuario_creador', 'usuario_aprobador', 
            'usuario_procesador', 'fecha_aprobacion', 'fecha_procesamiento',
            'created_at', 'updated_at'
        ]

class AjusteFinancieroCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para crear y actualizar ajustes financieros"""
    
    class Meta:
        model = AjusteFinanciero
        fields = [
            'fecha_ajuste', 'fecha_valor', 'tipo_ajuste', 'cuenta_debito', 
            'cuenta_credito', 'monto', 'moneda', 'concepto', 'descripcion', 
            'justificacion', 'observaciones', 'prioridad', 'fecha_vencimiento',
            'numero_documento_origen', 'referencia_externa', 'centro_costo'
        ]
    
    def validate(self, data):
        """Validaciones personalizadas"""
        # Validar que las cuentas de débito y crédito sean diferentes
        if data.get('cuenta_debito') == data.get('cuenta_credito'):
            raise serializers.ValidationError(
                "La cuenta de débito y crédito no pueden ser la misma."
            )
        
        # Validar que ambas cuentas estén activas
        if data.get('cuenta_debito') and not data['cuenta_debito'].activo:
            raise serializers.ValidationError(
                "La cuenta de débito seleccionada no está activa."
            )
        
        if data.get('cuenta_credito') and not data['cuenta_credito'].activo:
            raise serializers.ValidationError(
                "La cuenta de crédito seleccionada no está activa."
            )
        
        # Validar que el tipo de ajuste esté activo
        if data.get('tipo_ajuste') and not data['tipo_ajuste'].activo:
            raise serializers.ValidationError(
                "El tipo de ajuste seleccionado no está activo."
            )
        
        return data
    
    def create(self, validated_data):
        # Asignar el usuario creador
        validated_data['usuario_creador'] = self.context['request'].user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # Solo permitir actualización si el ajuste puede ser editado
        if not instance.puede_ser_editado:
            raise serializers.ValidationError(
                "Este ajuste no puede ser editado en su estado actual."
            )
        return super().update(instance, validated_data)

class CambiarEstadoAjusteSerializer(serializers.Serializer):
    """Serializer para cambiar el estado de un ajuste"""
    nuevo_estado = serializers.ChoiceField(choices=AjusteFinanciero.ESTADO_CHOICES)
    comentario = serializers.CharField(required=False, allow_blank=True)
    
    def validate_nuevo_estado(self, value):
        """Validar que el cambio de estado sea válido"""
        ajuste = self.context['ajuste']
        estado_actual = ajuste.estado
        
        # Definir transiciones válidas
        transiciones_validas = {
            'BORRADOR': ['PENDIENTE'],
            'PENDIENTE': ['APROBADO', 'RECHAZADO'],
            'APROBADO': ['PROCESADO', 'ANULADO'],
            'RECHAZADO': ['PENDIENTE'],
            'PROCESADO': ['ANULADO'],
            'ANULADO': [],
        }
        
        if value not in transiciones_validas.get(estado_actual, []):
            raise serializers.ValidationError(
                f"No es posible cambiar de {estado_actual} a {value}."
            )
        
        return value

class ExportarAjustesSerializer(serializers.Serializer):
    """Serializer para exportar ajustes"""
    formato = serializers.ChoiceField(choices=['excel', 'csv', 'pdf'])
    fecha_inicio = serializers.DateField(required=False)
    fecha_fin = serializers.DateField(required=False)
    estado = serializers.MultipleChoiceField(
        choices=AjusteFinanciero.ESTADO_CHOICES, 
        required=False
    )
    tipo_ajuste = serializers.PrimaryKeyRelatedField(
        queryset=TipoAjuste.objects.filter(activo=True),
        many=True,
        required=False
    )
    
    def validate(self, data):
        if data.get('fecha_inicio') and data.get('fecha_fin'):
            if data['fecha_inicio'] > data['fecha_fin']:
                raise serializers.ValidationError(
                    "La fecha de inicio no puede ser mayor que la fecha de fin."
                )
        return data
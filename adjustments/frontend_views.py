from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils.dateparse import parse_date
from .frontend_models import RegistroAjuste
from .frontend_serializers import RegistroAjusteSerializer, UserSimpleSerializer

class StandardResultsSetPagination(PageNumberPagination):
    """Paginación estándar que retorna el formato esperado por el frontend"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        return Response({
            'registros': data,
            'total': self.page.paginator.count,
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'page_size': self.page_size,
            'total_pages': self.page.paginator.num_pages
        })

class RegistroAjusteViewSet(viewsets.ModelViewSet):
    """ViewSet para los registros de ajustes compatible con el frontend Svelte"""
    queryset = RegistroAjuste.objects.all()
    serializer_class = RegistroAjusteSerializer
    permission_classes = [permissions.AllowAny]  # Permitir acceso sin autenticación para pruebas
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filtrar registros según parámetros de consulta"""
        queryset = RegistroAjuste.objects.all()
        
        # Filtros de búsqueda
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(id_cuenta__icontains=search) |
                Q(id_acuerdo_servicio__icontains=search) |
                Q(asesor_que_ajusto__icontains=search) |
                Q(justificacion__icontains=search)
            )
        
        # Filtro por fecha
        fecha_desde = self.request.query_params.get('fecha_desde', None)
        fecha_hasta = self.request.query_params.get('fecha_hasta', None)
        
        if fecha_desde:
            fecha_desde_parsed = parse_date(fecha_desde)
            if fecha_desde_parsed:
                queryset = queryset.filter(fecha_ajuste__gte=fecha_desde_parsed)
                
        if fecha_hasta:
            fecha_hasta_parsed = parse_date(fecha_hasta)
            if fecha_hasta_parsed:
                queryset = queryset.filter(fecha_ajuste__lte=fecha_hasta_parsed)
        
        # Filtro por asesor
        asesor = self.request.query_params.get('asesor', None)
        if asesor:
            queryset = queryset.filter(asesor_que_ajusto__icontains=asesor)
            
        # Filtro por cuenta
        cuenta = self.request.query_params.get('cuenta', None)
        if cuenta:
            queryset = queryset.filter(id_cuenta__icontains=cuenta)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """Asignar el usuario que crea el registro"""
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Obtener estadísticas de los registros"""
        queryset = self.get_queryset()
        total_registros = queryset.count()
        total_valor = sum(registro.valor_ajustado for registro in queryset)
        
        return Response({
            'total_registros': total_registros,
            'total_valor': total_valor,
            'promedio_valor': total_valor / total_registros if total_registros > 0 else 0
        })
    
    @action(detail=False, methods=['get'])
    def asesores(self, request):
        """Obtener lista de asesores únicos"""
        asesores = RegistroAjuste.objects.values_list('asesor_que_ajusto', flat=True).distinct()
        return Response({
            'asesores': list(asesores)
        })
        
    @action(detail=False, methods=['get'])
    def cuentas(self, request):
        """Obtener lista de cuentas únicas"""
        cuentas = RegistroAjuste.objects.values_list('id_cuenta', flat=True).distinct()
        return Response({
            'cuentas': list(cuentas)
        })

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para usuarios compatible con el frontend"""
    queryset = User.objects.all()
    serializer_class = UserSimpleSerializer
    permission_classes = [permissions.AllowAny]  # Permitir acceso sin autenticación para pruebas
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Obtener información del usuario actual"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
from django.shortcuts import get_object_or_404
from django.db.models import Count, Sum, Avg, Q
from django.db.models.functions import TruncMonth, TruncWeek, TruncDay
from django.utils import timezone
from datetime import datetime, timedelta
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from adjustments.models import AjusteFinanciero, TipoAjuste, CuentaContable
from .models import DashboardMetric, ReportTemplate, ReportExecution, UserActivity

class DashboardView(APIView):
    """Vista principal del dashboard con métricas resumidas"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # Período por defecto: últimos 30 días
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
        
        # Parámetros opcionales de fecha
        if request.GET.get('start_date'):
            start_date = datetime.strptime(request.GET['start_date'], '%Y-%m-%d').date()
        if request.GET.get('end_date'):
            end_date = datetime.strptime(request.GET['end_date'], '%Y-%m-%d').date()
        
        # Queryset base
        queryset = AjusteFinanciero.objects.filter(
            fecha_ajuste__date__range=[start_date, end_date]
        )
        
        # Métricas principales
        total_ajustes = queryset.count()
        monto_total = queryset.aggregate(total=Sum('monto'))['total'] or 0
        
        # Por estado
        por_estado = queryset.values('estado').annotate(
            cantidad=Count('id'),
            monto=Sum('monto')
        )
        
        # Por tipo de ajuste
        por_tipo = queryset.values(
            'tipo_ajuste__nombre'
        ).annotate(
            cantidad=Count('id'),
            monto=Sum('monto')
        )
        
        # Por prioridad
        por_prioridad = queryset.values('prioridad').annotate(
            cantidad=Count('id')
        )
        
        # Ajustes recientes (últimos 10)
        ajustes_recientes = queryset.select_related(
            'tipo_ajuste', 'usuario_creador'
        ).order_by('-fecha_ajuste')[:10]
        
        # Ajustes pendientes de aprobación
        pendientes_aprobacion = AjusteFinanciero.objects.filter(
            estado='PENDIENTE'
        ).count()
        
        # Promedio de tiempo de procesamiento (en días)
        ajustes_procesados = AjusteFinanciero.objects.filter(
            estado='PROCESADO',
            fecha_procesamiento__isnull=False,
            fecha_ajuste__isnull=False
        )
        
        tiempo_promedio = None
        if ajustes_procesados.exists():
            tiempos = []
            for ajuste in ajustes_procesados:
                diff = ajuste.fecha_procesamiento.date() - ajuste.fecha_ajuste.date()
                tiempos.append(diff.days)
            tiempo_promedio = sum(tiempos) / len(tiempos) if tiempos else 0
        
        return Response({
            'periodo': {
                'start_date': start_date,
                'end_date': end_date
            },
            'metricas_principales': {
                'total_ajustes': total_ajustes,
                'monto_total': float(monto_total),
                'pendientes_aprobacion': pendientes_aprobacion,
                'tiempo_promedio_procesamiento': tiempo_promedio
            },
            'distribucion': {
                'por_estado': list(por_estado),
                'por_tipo': list(por_tipo),
                'por_prioridad': list(por_prioridad)
            },
            'ajustes_recientes': [
                {
                    'id': ajuste.id,
                    'numero_ajuste': ajuste.numero_ajuste,
                    'concepto': ajuste.concepto,
                    'monto': float(ajuste.monto),
                    'estado': ajuste.estado,
                    'tipo_ajuste': ajuste.tipo_ajuste.get_nombre_display(),
                    'usuario_creador': ajuste.usuario_creador.get_full_name() or ajuste.usuario_creador.username,
                    'fecha_ajuste': ajuste.fecha_ajuste
                }
                for ajuste in ajustes_recientes
            ]
        })

class KPIsView(APIView):
    """Vista para KPIs específicos"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # Período por defecto: últimos 30 días
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
        
        # Parámetros opcionales
        if request.GET.get('start_date'):
            start_date = datetime.strptime(request.GET['start_date'], '%Y-%m-%d').date()
        if request.GET.get('end_date'):
            end_date = datetime.strptime(request.GET['end_date'], '%Y-%m-%d').date()
        
        queryset = AjusteFinanciero.objects.filter(
            fecha_ajuste__date__range=[start_date, end_date]
        )
        
        # KPI 1: Tasa de aprobación
        total_enviados = queryset.exclude(estado='BORRADOR').count()
        total_aprobados = queryset.filter(estado__in=['APROBADO', 'PROCESADO']).count()
        tasa_aprobacion = (total_aprobados / total_enviados * 100) if total_enviados > 0 else 0
        
        # KPI 2: Tiempo promedio de aprobación
        ajustes_aprobados = queryset.filter(
            estado__in=['APROBADO', 'PROCESADO'],
            fecha_aprobacion__isnull=False
        )
        
        tiempo_promedio_aprobacion = None
        if ajustes_aprobados.exists():
            tiempos = []
            for ajuste in ajustes_aprobados:
                diff = ajuste.fecha_aprobacion.date() - ajuste.fecha_ajuste.date()
                tiempos.append(diff.days)
            tiempo_promedio_aprobacion = sum(tiempos) / len(tiempos) if tiempos else 0
        
        # KPI 3: Ajustes por usuario top 5
        por_usuario = queryset.values(
            'usuario_creador__first_name',
            'usuario_creador__last_name',
            'usuario_creador__username'
        ).annotate(
            cantidad=Count('id'),
            monto_total=Sum('monto')
        ).order_by('-cantidad')[:5]
        
        # KPI 4: Montos por moneda
        por_moneda = queryset.values('moneda').annotate(
            cantidad=Count('id'),
            monto_total=Sum('monto')
        )
        
        # KPI 5: Eficiencia por día de la semana
        por_dia_semana = queryset.annotate(
            dia_semana=TruncDay('fecha_ajuste')
        ).values('dia_semana').annotate(
            cantidad=Count('id')
        ).order_by('dia_semana')
        
        return Response({
            'periodo': {
                'start_date': start_date,
                'end_date': end_date
            },
            'kpis': {
                'tasa_aprobacion': round(tasa_aprobacion, 2),
                'tiempo_promedio_aprobacion': tiempo_promedio_aprobacion,
                'total_ajustes_periodo': queryset.count(),
                'monto_total_periodo': float(queryset.aggregate(Sum('monto'))['monto'] or 0)
            },
            'rankings': {
                'usuarios_mas_activos': [
                    {
                        'usuario': f"{item['usuario_creador__first_name']} {item['usuario_creador__last_name']}".strip() or item['usuario_creador__username'],
                        'cantidad': item['cantidad'],
                        'monto_total': float(item['monto_total'] or 0)
                    }
                    for item in por_usuario
                ],
                'distribucion_monedas': list(por_moneda)
            },
            'tendencias': {
                'actividad_diaria': list(por_dia_semana)
            }
        })

class MonthlyChartView(APIView):
    """Vista para gráfico mensual"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # Últimos 12 meses por defecto
        end_date = timezone.now().date()
        start_date = end_date.replace(day=1) - timedelta(days=365)
        
        datos_mensuales = AjusteFinanciero.objects.filter(
            fecha_ajuste__date__range=[start_date, end_date]
        ).annotate(
            mes=TruncMonth('fecha_ajuste')
        ).values('mes').annotate(
            cantidad=Count('id'),
            monto=Sum('monto')
        ).order_by('mes')
        
        return Response({
            'datos_mensuales': [
                {
                    'mes': item['mes'].strftime('%Y-%m'),
                    'cantidad': item['cantidad'],
                    'monto': float(item['monto'] or 0)
                }
                for item in datos_mensuales
            ]
        })

class TypeChartView(APIView):
    """Vista para gráfico por tipo de ajuste"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # Período por defecto: últimos 30 días
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
        
        if request.GET.get('start_date'):
            start_date = datetime.strptime(request.GET['start_date'], '%Y-%m-%d').date()
        if request.GET.get('end_date'):
            end_date = datetime.strptime(request.GET['end_date'], '%Y-%m-%d').date()
        
        datos_tipo = AjusteFinanciero.objects.filter(
            fecha_ajuste__date__range=[start_date, end_date]
        ).values(
            'tipo_ajuste__nombre'
        ).annotate(
            cantidad=Count('id'),
            monto=Sum('monto')
        ).order_by('-cantidad')
        
        return Response({
            'datos_por_tipo': [
                {
                    'tipo': item['tipo_ajuste__nombre'],
                    'cantidad': item['cantidad'],
                    'monto': float(item['monto'] or 0)
                }
                for item in datos_tipo
            ]
        })

class AccountChartView(APIView):
    """Vista para gráfico por cuenta contable"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # Período por defecto: últimos 30 días
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
        
        if request.GET.get('start_date'):
            start_date = datetime.strptime(request.GET['start_date'], '%Y-%m-%d').date()
        if request.GET.get('end_date'):
            end_date = datetime.strptime(request.GET['end_date'], '%Y-%m-%d').date()
        
        # Top 10 cuentas más utilizadas como débito
        cuentas_debito = AjusteFinanciero.objects.filter(
            fecha_ajuste__date__range=[start_date, end_date]
        ).values(
            'cuenta_debito__codigo',
            'cuenta_debito__nombre'
        ).annotate(
            cantidad=Count('id'),
            monto=Sum('monto')
        ).order_by('-cantidad')[:10]
        
        # Top 10 cuentas más utilizadas como crédito
        cuentas_credito = AjusteFinanciero.objects.filter(
            fecha_ajuste__date__range=[start_date, end_date]
        ).values(
            'cuenta_credito__codigo',
            'cuenta_credito__nombre'
        ).annotate(
            cantidad=Count('id'),
            monto=Sum('monto')
        ).order_by('-cantidad')[:10]
        
        return Response({
            'cuentas_debito': [
                {
                    'cuenta': f"{item['cuenta_debito__codigo']} - {item['cuenta_debito__nombre']}",
                    'cantidad': item['cantidad'],
                    'monto': float(item['monto'] or 0)
                }
                for item in cuentas_debito
            ],
            'cuentas_credito': [
                {
                    'cuenta': f"{item['cuenta_credito__codigo']} - {item['cuenta_credito__nombre']}",
                    'cantidad': item['cantidad'],
                    'monto': float(item['monto'] or 0)
                }
                for item in cuentas_credito
            ]
        })

class SummaryReportView(APIView):
    """Vista para reporte resumen"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # Implementar reporte resumen
        return Response({
            'message': 'Reporte resumen - Por implementar',
            'tipo': 'resumen'
        })

class DetailedReportView(APIView):
    """Vista para reporte detallado"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # Implementar reporte detallado
        return Response({
            'message': 'Reporte detallado - Por implementar',
            'tipo': 'detallado'
        })

class ExportReportView(APIView):
    """Vista para exportar reportes"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        # Implementar exportación de reportes
        return Response({
            'message': 'Exportación de reportes - Por implementar',
            'formato': request.data.get('formato', 'pdf')
        })

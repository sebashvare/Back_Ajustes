"""
Analytics app URL configuration.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Dashboard KPIs
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('kpis/', views.KPIsView.as_view(), name='kpis'),
    
    # Charts and graphs
    path('charts/monthly/', views.MonthlyChartView.as_view(), name='monthly_chart'),
    path('charts/by-type/', views.TypeChartView.as_view(), name='type_chart'),
    path('charts/by-account/', views.AccountChartView.as_view(), name='account_chart'),
    
    # Reports
    path('reports/summary/', views.SummaryReportView.as_view(), name='summary_report'),
    path('reports/detailed/', views.DetailedReportView.as_view(), name='detailed_report'),
    path('reports/export/', views.ExportReportView.as_view(), name='export_report'),
]
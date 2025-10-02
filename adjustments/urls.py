"""
Adjustments app URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.AjusteFinancieroViewSet, basename='ajuste')

urlpatterns = [
    # Additional custom endpoints
    path('export/', views.ExportAjustesView.as_view(), name='export_ajustes'),
    path('import/', views.ImportAjustesView.as_view(), name='import_ajustes'),
    path('bulk-delete/', views.BulkDeleteView.as_view(), name='bulk_delete'),
    
    # Router URLs
    path('', include(router.urls)),
]
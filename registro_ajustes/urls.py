"""
URL configuration for registro_ajustes project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
# from rest_framework.documentation import include_docs_urls  # Comentado temporalmente

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API URLs para el frontend Svelte
    path('', include('adjustments.frontend_urls')),
    
    # API URLs originales
    path('api/auth/', include('authentication.urls')),
    path('api/adjustments/', include('adjustments.urls')),
    path('api/analytics/', include('analytics.urls')),
    
    # API Documentation - Comentado temporalmente
    # path('api/docs/', include_docs_urls(title='Registro Ajustes API')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
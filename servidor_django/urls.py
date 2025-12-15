from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from miapp.views import SubmissionCreateView, buscar_qr

"""
Configuración principal de URLs del proyecto Django.

Este archivo define las rutas globales del proyecto, incluyendo:
- Acceso al panel de administración.
- Inclusión de las URLs de la aplicación principal.
- Rutas directas a vistas específicas.
- Configuración para servir archivos multimedia en entorno de desarrollo.

Main URL configuration for the Django project.

This file defines the global routes of the project, including:
- Access to the admin panel.
- Inclusion of application URLs.
- Direct access to specific views.
- Configuration for serving media files in development environments.
"""

urlpatterns = [
    path(
        'admin/',
        admin.site.urls
    ),
    path(
        'api/',
        include('miapp.urls')
    ),
    path(
        'buscar/',
        buscar_qr,
        name='buscar-qr'
    ),
]

if settings.DEBUG:
    """
    Configuración para servir archivos multimedia en modo desarrollo.

    Cuando DEBUG está habilitado, Django sirve los archivos multimedia
    directamente desde MEDIA_ROOT utilizando MEDIA_URL.

    Media files configuration for development mode.

    When DEBUG is enabled, Django serves media files directly from
    MEDIA_ROOT using MEDIA_URL.
    """
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )

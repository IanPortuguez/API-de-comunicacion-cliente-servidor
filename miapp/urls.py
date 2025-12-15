from django.urls import path
from .views import SubmissionCreateView, buscar_qr

"""
Configuración de rutas (URLs) de la aplicación.

Este archivo define los endpoints disponibles tanto para la API REST
como para las vistas basadas en plantillas HTML.

Configuration of application URLs.

This file defines the available endpoints for both the REST API
and template-based HTML views.
"""

urlpatterns = [
    path(
        'submit/',
        SubmissionCreateView.as_view(),
        name='submission-create'
    ),
    path(
        'buscar/',
        buscar_qr,
        name='buscar-qr'
    ),
]

from django.urls import path
from .views import SubmissionCreateView, buscar_qr

urlpatterns = [
    path('submit/', SubmissionCreateView.as_view(), name='submission-create'),
    path('buscar/', buscar_qr, name='buscar-qr'),
]

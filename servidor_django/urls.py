from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from miapp.views import SubmissionCreateView, buscar_qr

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('miapp.urls')),
    path('buscar/', buscar_qr, name='buscar-qr'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

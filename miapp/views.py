from rest_framework import generics, status
from rest_framework.response import Response
from .models import Submission
from .serializers import SubmissionSerializer
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseBadRequest



class SubmissionCreateView(generics.CreateAPIView):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print(serializer.errors)  # ← esto te dice qué campo falla
            return Response(serializer.errors, status=400)
        submission = serializer.save()
        return Response(serializer.data, status=201)


    """
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            submission = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            # 🔧 En modo abierto, devuelve 200 con mensaje de error parcial
            return Response({
                "status": "warning",
                "message": str(e),
                "received_data": request.data
            }, status=status.HTTP_200_OK)
    """
def buscar_qr(request):
    """
    Vista que responde GET. Espera un parámetro 'qr' en querystring o formulario.
     Si se envía, busca el Submission con qr exacto y devuelve sus relaciones.
    """
    qr_code = request.GET.get('qr', '').strip()  # permitimos GET (formulario) y limpiamos espacios
    context = {'query': qr_code, 'found': False}

    if qr_code:
        # Usamos get for exact match. Si no se encuentra, get_object_or_404 lanza 404.
        # Alternativa: Submission.objects.filter(qr__iexact=qr_code).first() para manejar nulls en la UI.
        submission = Submission.objects.filter(qr=qr_code).first()
        if submission:
            context['found'] = True
            context['submission'] = submission
            context['photos'] = submission.photos.all()
            context['audios'] = submission.audio.all()
            context['route'] = submission.route.all()
        else:
            context['error'] = "No se encontró ningún registro con ese código QR."

    return render(request, 'miapp/busqueda.html', context)
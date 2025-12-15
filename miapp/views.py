from rest_framework import generics, status
from rest_framework.response import Response
from .models import Submission
from .serializers import (
    SubmissionSerializer,
    PhotoSerializer,
    AudioSerializer,
    RoutePointSerializer
)
from django.shortcuts import render


class SubmissionCreateView(generics.CreateAPIView):
    """
    Vista para la creación de Submissions mediante la API.

    Esta vista permite recibir una solicitud POST con toda la información
    necesaria para crear una Submission junto con sus relaciones
    (fotografías, audios y puntos de ruta) utilizando serializers anidados.

    Submission creation view for the API.

    This view handles POST requests containing all required data to create
    a Submission along with its related entities (photos, audio, and route points)
    using nested serializers.
    """

    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer

    def create(self, request, *args, **kwargs):
        """
        Maneja la creación de una Submission.

        Valida los datos de entrada, crea la Submission y retorna la
        respuesta correspondiente con el estado HTTP adecuado.

        Handles Submission creation.

        Validates input data, creates the Submission, and returns the
        appropriate HTTP response.
        """
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            # Se imprime el error para depuración en entorno de desarrollo
            # Error is printed for debugging purposes in development
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        submission = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


def buscar_qr(request):
    """
    Vista basada en función para la búsqueda de una Submission por código QR.

    Esta vista recibe un código QR mediante parámetros GET, busca el registro
    correspondiente y retorna los datos asociados (fotografías, audios y ruta)
    renderizados en una plantilla HTML.

    Function-based view to search for a Submission by QR code.

    This view receives a QR code via GET parameters, searches for the
    corresponding record, and renders associated data (photos, audio, and route)
    in an HTML template.
    """

    qr_code = request.GET.get('qr', '').strip()
    context = {
        'query': qr_code,
        'found': False
    }

    if qr_code:
        submission = Submission.objects.filter(qr=qr_code).first()

        if submission:
            context['found'] = True
            context['submission'] = submission

            # Se utilizan serializers para devolver los archivos en Base64
            # Serializers are used to return files encoded in Base64
            context['photos'] = PhotoSerializer(
                submission.photos.all(), many=True
            ).data
            context['audios'] = AudioSerializer(
                submission.audio.all(), many=True
            ).data
            context['route'] = RoutePointSerializer(
                submission.route.all(), many=True
            ).data
        else:
            context['error'] = (
                "No se encontró ningún registro con ese código QR. "
                "No record was found with the provided QR code."
            )

    return render(request, 'miapp/busqueda.html', context)

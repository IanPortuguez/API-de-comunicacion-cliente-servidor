from rest_framework import serializers
from .models import Submission, Photo, Audio, RoutePoint
from django.core.files.base import ContentFile
from django.utils.dateparse import parse_datetime
import base64, uuid, filetype
from datetime import datetime


class PhotoSerializer(serializers.ModelSerializer):
    """
    Serializador de fotografías asociadas a una Submission.

    Este serializer permite recibir imágenes codificadas en Base64,
    decodificarlas, almacenarlas en el sistema de archivos y devolverlas
    nuevamente como una URL Base64 para su consumo en el frontend.

    Photo serializer associated with a Submission.

    This serializer allows receiving Base64-encoded images, decoding them,
    storing them on the file system, and returning them as Base64 URLs
    for frontend consumption.
    """

    base64 = serializers.CharField(write_only=True, required=False)
    url = serializers.SerializerMethodField(read_only=True)
    timestamp = serializers.DateTimeField(required=False)

    class Meta:
        model = Photo
        fields = ('base64', 'latitude', 'longitude', 'timestamp', 'url')

    def get_url(self, obj):
        """
        Devuelve la imagen almacenada como una cadena Base64.

        Returns the stored image as a Base64 string.
        """
        if obj.file:
            with open(obj.file.path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode()
            ext = obj.file.name.split('.')[-1]
            return f"data:image/{ext};base64,{encoded}"
        return None


class AudioSerializer(serializers.ModelSerializer):
    """
    Serializador de archivos de audio asociados a una Submission.

    Permite recibir audios codificados en Base64, almacenarlos y
    devolverlos nuevamente en formato Base64.

    Audio serializer associated with a Submission.

    Allows receiving Base64-encoded audio files, storing them, and
    returning them again in Base64 format.
    """

    base64 = serializers.CharField(write_only=True, required=False)
    url = serializers.SerializerMethodField(read_only=True)
    date = serializers.CharField(required=False)

    class Meta:
        model = Audio
        fields = ('base64', 'date', 'url')

    def get_url(self, obj):
        """
        Devuelve el archivo de audio almacenado como una cadena Base64.

        Returns the stored audio file as a Base64 string.
        """
        if obj.file:
            with open(obj.file.path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode()
            ext = obj.file.name.split('.')[-1]
            return f"data:audio/{ext};base64,{encoded}"
        return None


class RoutePointSerializer(serializers.ModelSerializer):
    """
    Serializador para puntos geográficos de una ruta.

    Representa coordenadas que conforman una ruta asociada a una Submission.

    Serializer for geographic route points.

    Represents coordinates that define a route associated with a Submission.
    """

    class Meta:
        model = RoutePoint
        fields = ('lat', 'lon')


class SubmissionSerializer(serializers.ModelSerializer):
    """
    Serializador principal del sistema.

    Gestiona la creación completa de una Submission junto con sus
    relaciones (fotografías, audios y puntos de ruta) en una sola solicitud.

    Main serializer of the system.

    Handles the full creation of a Submission along with its related
    entities (photos, audio, and route points) in a single request.
    """

    photos = PhotoSerializer(many=True, required=False)
    audio = AudioSerializer(many=True, required=False)
    route = RoutePointSerializer(many=True, required=False)
    notes = serializers.JSONField(required=False)

    class Meta:
        model = Submission
        fields = (
            'id', 'qr', 'user', 'registered_user',
            'photos', 'notes', 'audio', 'route', 'created_at'
        )
        read_only_fields = ('id', 'created_at')

    def to_internal_value(self, data):
        """
        Filtra el JSON de entrada para aceptar únicamente campos definidos
        en el serializer, evitando errores por campos desconocidos.

        Filters incoming JSON to accept only fields defined
        in the serializer, preventing errors from unknown fields.
        """
        if not isinstance(data, dict):
            raise serializers.ValidationError("Formato de JSON inválido / Invalid JSON format")

        known = set(self.fields.keys())
        filtered = {k: v for k, v in data.items() if k in known}
        return super().to_internal_value(filtered)

    def create(self, validated_data):
        """
        Crea una Submission junto con todas sus relaciones asociadas.

        Proceso:
        - Crea la Submission principal.
        - Decodifica y guarda fotografías.
        - Decodifica y guarda audios.
        - Registra los puntos de ruta.

        Creates a Submission along with all its associated relations.

        Process:
        - Creates the main Submission.
        - Decodes and saves photos.
        - Decodes and saves audio files.
        - Registers route points.
        """
        photos_data = validated_data.pop('photos', [])
        audio_data = validated_data.pop('audio', [])
        route_data = validated_data.pop('route', [])

        submission = Submission.objects.create(**validated_data)

        # Guardar fotos / Save photos
        for p in photos_data:
            b64 = p.pop('base64', None)
            ts_raw = p.pop('timestamp', None)
            timestamp = parse_datetime(ts_raw) if ts_raw else None

            if b64:
                content_file, ext = self._get_contentfile_and_ext(b64)
                filename = f"{uuid.uuid4().hex}.{ext}"
                photo = Photo(
                    submission=submission,
                    latitude=p.get('latitude'),
                    longitude=p.get('longitude'),
                    timestamp=timestamp
                )
                photo.file.save(filename, content_file, save=True)

        # Guardar audios / Save audio files
        for a in audio_data:
            b64 = a.pop('base64', None)
            date_str = a.pop('date', None)
            dt = parse_datetime(date_str) if date_str else datetime.now()

            if b64:
                content_file, ext = self._get_contentfile_and_ext(b64, is_image=False)
                filename = f"{uuid.uuid4().hex}.{ext}"
                audio = Audio(submission=submission, date=dt)
                audio.file.save(filename, content_file, save=True)

        # Guardar ruta / Save route points
        for r in route_data:
            RoutePoint.objects.create(
                submission=submission,
                lat=r.get('lat'),
                lon=r.get('lon')
            )

        return submission

    def _get_contentfile_and_ext(self, b64_string, is_image=True):
        """
        Decodifica una cadena Base64 y determina su extensión de archivo.

        Decode a Base64 string and determine its file extension.
        """
        if b64_string.startswith('data:'):
            _, b64_string = b64_string.split(',', 1)

        try:
            decoded = base64.b64decode(b64_string)
        except Exception:
            raise serializers.ValidationError("Base64 inválido / Invalid Base64")

        kind = filetype.guess(decoded)

        if is_image:
            ext = kind.extension if kind else 'jpg'
        else:
            ext = kind.extension if kind else 'wav'

        return ContentFile(decoded), ext

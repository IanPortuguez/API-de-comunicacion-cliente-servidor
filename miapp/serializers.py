from rest_framework import serializers
from .models import Submission, Photo, Audio, RoutePoint
from django.core.files.base import ContentFile
from django.utils.dateparse import parse_datetime
import base64, uuid, filetype
from datetime import datetime

class PhotoSerializer(serializers.ModelSerializer):
    base64 = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Photo
        fields = ('base64', 'latitude', 'longitude')


class AudioSerializer(serializers.ModelSerializer):
    base64 = serializers.CharField(write_only=True, required=False)
    date = serializers.CharField(required=False)

    class Meta:
        model = Audio
        fields = ('base64', 'date')


class RoutePointSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoutePoint
        fields = ('lat', 'lon')


class SubmissionSerializer(serializers.ModelSerializer):
    photos = PhotoSerializer(many=True, required=False)
    audio = AudioSerializer(many=True, required=False)
    route = RoutePointSerializer(many=True, required=False)

    # Ahora es un string base64, no una lista
    fingerprint_binary = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True
    )

    notes = serializers.JSONField(required=False)

    class Meta:
        model = Submission
        fields = (
            'id', 'qr', 'user', 'fingerprint_taken', 'fingerprint_binary',
            'photos', 'notes', 'audio', 'route', 'created_at'
        )
        read_only_fields = ('id', 'created_at')

    def to_internal_value(self, data):
        if not isinstance(data, dict):
            raise serializers.ValidationError("Formato de JSON inválido")

        known = set(self.fields.keys())
        filtered = {k: v for k, v in data.items() if k in known}

        # ✅ Convertir base64 a lista de ints
        fp = data.get("fingerprint_binary")
        if fp is not None:
            filtered["fingerprint_binary"] = fp  # Guardamos la cadena base64 tal cual

        return super().to_internal_value(filtered)

    # resto del código sin cambios ↓↓↓


    def create(self, validated_data):
        photos_data = validated_data.pop('photos', [])
        audio_data = validated_data.pop('audio', [])
        route_data = validated_data.pop('route', [])
        submission = Submission.objects.create(**validated_data)

        # Fotos
        for p in photos_data:
            b64 = p.pop('base64', None)
            if b64:
                content_file, ext = self._get_contentfile_and_ext(b64)
                filename = f"{uuid.uuid4().hex}.{ext}"
                # Guardar usando el campo ImageField, que usará DEFAULT_FILE_STORAGE
                photo = Photo(submission=submission, latitude=p.get('latitude'), longitude=p.get('longitude'))
                photo.file.save(filename, content_file, save=True)

        # Audios
        for a in audio_data:
            b64 = a.pop('base64', None)
            if b64:
                date_str = a.pop('date', None)
                dt = parse_datetime(date_str) if date_str else datetime.now()
                content_file, ext = self._get_contentfile_and_ext(b64, is_image=False)
                filename = f"{uuid.uuid4().hex}.{ext}"
                audio = Audio(submission=submission, date=dt)
                audio.file.save(filename, content_file, save=True)

        # Ruta
        for r in route_data:
            RoutePoint.objects.create(submission=submission, lat=r.get('lat'), lon=r.get('lon'))

        return submission

    def _get_contentfile_and_ext(self, b64_string, is_image=True):
        """
        Devuelve (ContentFile, extension) a partir de Base64.
        Maneja data:header si viene incluida.
        """
        if b64_string.startswith('data:'):
            _, b64_string = b64_string.split(',', 1)
        try:
            decoded = base64.b64decode(b64_string)
        except Exception:
            raise serializers.ValidationError("Base64 inválido")

        # Detectar tipo con filetype (bytes)
        kind = filetype.guess(decoded)
        if is_image:
            ext = kind.extension if kind else 'jpg'
        else:
            ext = kind.extension if kind else 'wav'

        return ContentFile(decoded), ext
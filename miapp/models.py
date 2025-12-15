from django.db import models
from django.utils import timezone


class Submission(models.Model):
    """
    Modelo Submission.

    Modelo principal del sistema al cual se relacionan otros modelos.
    Su propósito es agrupar y vincular datos que provienen de una misma
    fuente, identificados mediante un código QR.

    Este modelo actúa como la entidad central para la consulta y
    organización de la información relacionada a una submission.

    Submission model.

    Main system model to which other models are related.
    Its purpose is to group and link data coming from the same source,
    identified by a QR code.

    This model acts as the central entity for querying and organizing
    information related to a submission.
    """

    registered_user = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Nombre del encargado que realizó la venta. / Name of the staff member who performed the sale."
    )
    qr = models.CharField(
        max_length=100,
        help_text="Representación en texto del código QR. / Text representation of the QR code."
    )
    user = models.CharField(
        max_length=50,
        help_text="Nombre del cliente al que se le realizó la venta. / Name of the customer to whom the product was sold."
    )
    notes = models.JSONField(
        default=list,
        help_text="Lista de notas o valores de texto asociados a la submission. / List of notes or text values associated with the submission."
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        help_text="Fecha y hora de creación del registro. / Date and time when the record was created."
    )

    def __str__(self):
        return f"{self.qr} - {self.created_at.isoformat()}"


class Photo(models.Model):
    """
    Modelo Photo.

    Representa una fotografía asociada a una submission, incluyendo
    información geográfica y temporal.

    Photo model.

    Represents a photo associated with a submission, including
    geographic and temporal information.
    """

    submission = models.ForeignKey(
        Submission,
        related_name='photos',
        on_delete=models.CASCADE,
        help_text="Submission a la que pertenece la fotografía. / Submission to which the photo belongs."
    )
    file = models.ImageField(
        upload_to='photos/',
        help_text="Archivo de imagen asociado a la submission. / Image file associated with the submission."
    )
    latitude = models.FloatField(
        help_text="Latitud donde fue tomada la fotografía. / Latitude where the photo was taken."
    )
    longitude = models.FloatField(
        help_text="Longitud donde fue tomada la fotografía. / Longitude where the photo was taken."
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True,
        help_text="Fecha y hora en que se registró la fotografía. / Date and time when the photo was recorded."
    )

    def __str__(self):
        return f"Photo {self.id} for Submission {self.submission.id}"


class Audio(models.Model):
    """
    Modelo Audio.

    Representa un archivo de audio asociado a una submission.

    Audio model.

    Represents an audio file associated with a submission.
    """

    submission = models.ForeignKey(
        Submission,
        related_name='audio',
        on_delete=models.CASCADE,
        help_text="Submission a la que pertenece el archivo de audio. / Submission to which the audio file belongs."
    )
    file = models.FileField(
        upload_to='audio/',
        help_text="Archivo de audio asociado a la submission. / Audio file associated with the submission."
    )
    date = models.DateTimeField(
        help_text="Fecha y hora en que se registró el audio. / Date and time when the audio was recorded."
    )

    def __str__(self):
        return f"Audio {self.id} for Submission {self.submission.id}"


class RoutePoint(models.Model):
    """
    Modelo RoutePoint.

    Representa un punto geográfico que forma parte de una ruta
    asociada a una submission.

    RoutePoint model.

    Represents a geographic point that is part of a route
    associated with a submission.
    """

    submission = models.ForeignKey(
        Submission,
        related_name='route',
        on_delete=models.CASCADE,
        help_text="Submission a la que pertenece el punto de ruta. / Submission to which the route point belongs."
    )
    lat = models.FloatField(
        help_text="Latitud del punto geográfico. / Latitude of the geographical point."
    )
    lon = models.FloatField(
        help_text="Longitud del punto geográfico. / Longitude of the geographical point."
    )

    def __str__(self):
        return f"RoutePoint ({self.lat}, {self.lon}) for Submission {self.submission.id}"

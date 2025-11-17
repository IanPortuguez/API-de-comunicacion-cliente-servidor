from django.db import models
from django.utils import timezone

class Submission(models.Model):
    qr = models.CharField(max_length=1000)
    user = models.CharField(max_length=255)
    fingerprint_taken = models.BooleanField(default=False)
    fingerprint_binary = models.TextField(null=True, blank=True)
    notes = models.JSONField(default=list)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.qr} - {self.created_at.isoformat()}"


class Photo(models.Model):
    submission = models.ForeignKey(Submission, related_name='photos', on_delete=models.CASCADE)
    file = models.ImageField(upload_to='photos/')
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return f"Photo {self.id} for {self.submission.id}"


class Audio(models.Model):
    submission = models.ForeignKey(Submission, related_name='audio', on_delete=models.CASCADE)
    file = models.FileField(upload_to='audio/')
    date = models.DateTimeField()

    def __str__(self):
        return f"Audio {self.file},{self.date} for {self.submission.id}"


class RoutePoint(models.Model):
    submission = models.ForeignKey(Submission, related_name='route', on_delete=models.CASCADE)
    lat = models.FloatField()
    lon = models.FloatField()

    def __str__(self):
        return f"RoutePoint {self.lat},{self.lon} for {self.submission.id}"

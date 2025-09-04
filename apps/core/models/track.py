from django.db import models


class Track(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    length_km = models.FloatField()
    turns = models.IntegerField()
    photo = models.ImageField(upload_to="track_photos/", null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.location} ({self.length_km} km, {self.turns} turns)"
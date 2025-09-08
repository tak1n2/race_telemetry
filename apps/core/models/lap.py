from django.db import models

from apps.core.models import Driver, Track, Car


class Lap(models.Model):
    lap_number = models.IntegerField()
    lap_time = models.TimeField(help_text="Lap time in seconds")
    sector1_time = models.TimeField(null=True, blank=True)
    sector2_time = models.TimeField(null=True, blank=True)
    sector3_time = models.TimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    #
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name="laps")
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name="laps")
    car = models.ForeignKey(Car, on_delete=models.SET_NULL, null=True, blank=True, related_name="laps")

    def __str__(self):
        fastest = " (Fastest)" if self.is_fastest else ""
        return f"Lap {self.lap_number} - {self.lap_time:.3f}s{fastest}"
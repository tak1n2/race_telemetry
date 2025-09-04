from django.db import models

from apps.core.models.lap import Lap


class TelemetryPoint(models.Model):
    lap = models.ForeignKey(Lap, on_delete=models.CASCADE, related_name="telemetry")
    timestamp = models.FloatField(help_text="Seconds since lap start")
    speed = models.FloatField(help_text="km/h")
    throttle = models.FloatField(help_text="0-100%")
    brake = models.FloatField(help_text="0-100%")
    gear = models.IntegerField()
    rpm = models.IntegerField()
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"t={self.timestamp:.2f}s | {self.speed:.1f} km/h | Gear {self.gear}"
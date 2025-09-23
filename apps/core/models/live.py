from django.db import models
from .car import Car
from .driver import Driver
from .track import Track

class LiveSession(models.Model):
    session_uid = models.CharField(max_length=32, unique=True)   # ← було BigIntegerField
    car_label    = models.CharField(max_length=120, blank=True, null=True, default="—")
    driver_label = models.CharField(max_length=120, blank=True, null=True, default="—")
    track_label  = models.CharField(max_length=120, blank=True, null=True, default="—")
    started_at   = models.DateTimeField(auto_now_add=True)
    finished_at  = models.DateTimeField(blank=True, null=True)

class LiveLap(models.Model):
    session = models.ForeignKey(LiveSession, on_delete=models.CASCADE, related_name="laps")
    lap_number = models.IntegerField()
    lap_time_ms = models.IntegerField(null=True, blank=True)
    sector1_ms = models.IntegerField(null=True, blank=True)
    sector2_ms = models.IntegerField(null=True, blank=True)
    sector3_ms = models.IntegerField(null=True, blank=True)

class LiveTelemetryPoint(models.Model):
    lap = models.ForeignKey(LiveLap, on_delete=models.CASCADE, related_name="points")
    t_ms = models.IntegerField()
    speed_kmh = models.FloatField()
    rpm = models.IntegerField(null=True, blank=True)
    throttle = models.FloatField(null=True, blank=True)
    brake = models.FloatField(null=True, blank=True)
    gear = models.IntegerField(null=True, blank=True)

from django.db import models

class Lap(models.Model):
    lap_number = models.IntegerField()
    lap_time = models.FloatField(help_text="Lap time in seconds")
    sector1_time = models.FloatField(null=True, blank=True)
    sector2_time = models.FloatField(null=True, blank=True)
    sector3_time = models.FloatField(null=True, blank=True)
    is_fastest = models.BooleanField(default=False)

    def __str__(self):
        fastest = " (Fastest)" if self.is_fastest else ""
        return f"Lap {self.lap_number} - {self.lap_time:.3f}s{fastest}"
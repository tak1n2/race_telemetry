from django.db import models

class Lap(models.Model):
    lap_number = models.IntegerField()
    lap_time = models.TimeField(help_text="Lap time in seconds")
    sector1_time = models.TimeField(null=True, blank=True)
    sector2_time = models.TimeField(null=True, blank=True)
    sector3_time = models.TimeField(null=True, blank=True)

    def __str__(self):
        fastest = " (Fastest)" if self.is_fastest else ""
        return f"Lap {self.lap_number} - {self.lap_time:.3f}s{fastest}"
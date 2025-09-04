from django.db import models

class Car(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=120)
    maker = models.CharField(max_length=120)
    model = models.CharField(max_length=120)
    year = models.IntegerField()

    def __str__(self):
        return f"{self.maker} {self.model} ({self.year})"
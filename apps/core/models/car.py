from django.db import models

class Car(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=120)
    maker = models.CharField(max_length=120)
    model = models.CharField(max_length=120)
    year = models.IntegerField()
    rating = models.IntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.maker} {self.model} ({self.year})"

    @property
    def stars(self):
        if self.rating <= 10:
            return "★" * self.rating
        return f"<span class='f1-stars'>{'★' * self.rating}</span>"
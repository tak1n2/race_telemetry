from django.db import models

from apps.core.models.team import Team


class Driver(models.Model):
    # id
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    number = models.IntegerField()
    country = models.CharField(max_length=50)
    rating = models.IntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    #
    team = models.ForeignKey(Team, on_delete=models.CASCADE)



    def __str__(self):
        return f"#{self.number} {self.first_name} {self.last_name} ({self.team.name})"

    @property
    def stars(self):
        return "★" * self.rating
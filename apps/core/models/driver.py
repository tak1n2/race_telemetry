from django.db import models

class Team(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} ({self.country})"


class Driver(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    number = models.IntegerField()
    country = models.CharField(max_length=50)

    def __str__(self):
        return f"#{self.number} {self.first_name} {self.last_name} ({self.team.name})"
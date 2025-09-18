from django import forms
from apps.core.models import Driver, Team


class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = ["first_name", "last_name", "number", "country", "team"]


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ["name", "country"]
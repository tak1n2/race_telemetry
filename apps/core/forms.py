from django import forms
from apps.core.models import Driver, Team, Track, Car


class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = ["first_name", "last_name", "number", "country", "team", "rating"]

    def clean_rating(self):
        r = self.cleaned_data.get("rating")
        if not (1 <= r <= 10):
            raise forms.ValidationError("Rating must be between 1 and 10.")
        return r

class LiveSetupForm(forms.Form):
    car = forms.ModelChoiceField(queryset=Car.objects.all(), widget=forms.Select(attrs={"class":"input"}))
    driver = forms.ModelChoiceField(queryset=Driver.objects.all(), widget=forms.Select(attrs={"class":"input"}))
    track = forms.ModelChoiceField(queryset=Track.objects.all(), widget=forms.Select(attrs={"class":"input"}))

class LiveBindForm(forms.Form):
    car    = forms.ModelChoiceField(queryset=Car.objects.all(), required=False)
    driver = forms.ModelChoiceField(queryset=Driver.objects.all(), required=False)
    track  = forms.ModelChoiceField(queryset=Track.objects.all(), required=False)

class LapSimulationForm(forms.Form):
    car = forms.ModelChoiceField(queryset=Car.objects.all(), widget=forms.Select(attrs={"class": "input"}))
    driver = forms.ModelChoiceField(queryset=Driver.objects.all(), widget=forms.Select(attrs={"class": "input"}))
    track = forms.ModelChoiceField(queryset=Track.objects.all(), widget=forms.Select(attrs={"class": "input"}))


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ["name", "country"]

class TrackForm(forms.ModelForm):
    class Meta:
        model = Track
        fields = ["name", "location", "length_km", "turns", "photo"]


class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ["type", "maker", "model", "year", "rating"]

    def clean_rating(self):
        r = self.cleaned_data.get("rating")
        if r is None:
            return r
        if not (1 <= r <= 15):
            raise forms.ValidationError("Rating must be between 1 and 15.")
        return r
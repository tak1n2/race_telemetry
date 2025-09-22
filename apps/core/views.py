from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.decorators.http import require_http_methods

from apps.core.forms import TeamForm, DriverForm, TrackForm, CarForm, LapSimulationForm
from apps.core.models import Driver, Team, Track, Car
from apps.core.services.lap_sim import simulate_lap, build_speed_polyline, build_ticks_y, build_ticks_x


# Create your views here.
def about_view(request):
   return render(request, 'about.html')

def welcome_view(request):
    return render(request,'core/pages/welcome.html')

@require_http_methods(["GET","POST"])
@require_http_methods(["GET", "POST"])
def drivers(request):
    if request.method == "POST":
        form = DriverForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("drivers")

    context = {
        "driver_list": Driver.objects.all(),
        "teams": Team.objects.all(),
    }
    return render(request, "core/pages/drivers.html", context)

@require_http_methods(["GET", "POST"])
def teams(request):
    if request.method == "POST":
        form = TeamForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("teams")

    context = {
        "team_list": Team.objects.all(),
    }
    return render(request, "core/pages/teams.html", context)


@require_http_methods(["GET", "POST"])
def tracks(request):
    if request.method == "POST":
        form = TrackForm(request.POST, request.FILES)   # <— важливо: request.FILES
        if form.is_valid():
            form.save()
            return redirect("tracks")

    context = {
        "track_list": Track.objects.all().order_by("-created_at"),
        "track_form": TrackForm(),
    }
    return render(request, "core/pages/tracks.html", context)

@require_http_methods(["GET", "POST"])
def cars(request):
    if request.method == "POST":
        form = CarForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("cars")

    context = {
        "car_list": Car.objects.all().order_by("-created_at"),
    }
    return render(request, "core/pages/cars.html", context)


@require_http_methods(["GET", "POST"])
def lap_telemetry(request):
    sim = None
    form = LapSimulationForm(request.POST or None)
    track = car = driver = None
    sim_polyline = ""
    y_ticks = []
    x_ticks = []

    if request.method == "POST" and form.is_valid():
        car = form.cleaned_data["car"]
        driver = form.cleaned_data["driver"]
        track = form.cleaned_data["track"]

        sim = simulate_lap(
            length_km=track.length_km,
            turns=track.turns,
            car_rating=car.rating,
            driver_rating=driver.rating,
        )

        # константи графіка
        W, H, PAD = 1000, 260, 40
        Y_MIN, Y_MAX = 40.0, 360.0

        sim_polyline = build_speed_polyline(sim.points, w=W, h=H, pad=PAD, y_min=Y_MIN, y_max=Y_MAX)
        y_ticks = build_ticks_y(h=H, pad=PAD, y_min=Y_MIN, y_max=Y_MAX, step=40.0)
        x_ticks = build_ticks_x(sim.lap_time_sec, w=W, pad=PAD, parts=5)  # 0%,20%,...,100%

    return render(request, "core/pages/lap_telemetry.html", {
        "form": form,
        "sim": sim,
        "sim_polyline": sim_polyline,
        "y_ticks": y_ticks,
        "x_ticks": x_ticks,
        "track": track,
        "car": car,
        "driver": driver,
    })


class CarDetailUpdateView(View):
    def get(self, request, pk):
        car = get_object_or_404(Car, pk=pk)
        form = CarForm(instance=car)
        return render(request, "core/pages/car_detail.html", {"car_form": form, "car": car})

    def post(self, request, pk):
        car = get_object_or_404(Car, pk=pk)
        form = CarForm(request.POST, instance=car)
        if "submit_car" in request.POST and form.is_valid():
            form.save()
            return redirect("car_detail", pk=pk)
        return render(request, "core/pages/car_detail.html", {"car_form": form, "car": car})



class DriverDetailUpdateView(View):
    def get(self, request, pk):
        driver = get_object_or_404(Driver, pk=pk)
        driver_form = DriverForm(instance=driver)
        return render(request, "core/pages/driver_detail.html", {"driver_form": driver_form})

    def post(self, request, pk):
        driver = get_object_or_404(Driver, pk=pk)
        driver_form = DriverForm(request.POST, instance=driver)
        if "submit_driver" in request.POST:
            if driver_form.is_valid():
                driver_form.save()
                return redirect("driver_detail", pk=pk)
        return render(request, "core/pages/driver_detail.html", {"driver_form": driver_form})


class TeamDetailUpdateView(View):
    def get(self, request, pk):
        team = get_object_or_404(Team, pk=pk)
        team_form = TeamForm(instance=team)
        return render(request, "core/pages/team_detail.html", {"team_form": team_form})

    def post(self, request, pk):
        team = get_object_or_404(Team, pk=pk)
        team_form = TeamForm(request.POST, instance=team)
        if "submit_team" in request.POST:
            if team_form.is_valid():
                team_form.save()
                return redirect("team_detail", pk=pk)
        return render(request, "core/pages/team_detail.html", {"team_form": team_form})


class TrackDetailUpdateView(View):
    def get(self, request, pk):
        track = get_object_or_404(Track, pk=pk)
        form = TrackForm(instance=track)
        return render(request, "core/pages/track_detail.html", {"track_form": form, "track": track})

    def post(self, request, pk):
        track = get_object_or_404(Track, pk=pk)
        form = TrackForm(request.POST, request.FILES, instance=track)  # <— файли тут теж
        if "submit_track" in request.POST and form.is_valid():
            form.save()
            return redirect("track_detail", pk=pk)
        return render(request, "core/pages/track_detail.html", {"track_form": form, "track": track})
        
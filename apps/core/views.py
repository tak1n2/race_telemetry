import csv
import zipfile
from io import BytesIO

import json

import matplotlib.pyplot as plt
from django.contrib.auth.views import LoginView
from django.http import HttpResponse, JsonResponse, Http404, FileResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.decorators.http import require_http_methods
from django.views import generic

from apps.core.forms import TeamForm, DriverForm, TrackForm, CarForm, LapSimulationForm, LiveSetupForm, LiveBindForm
from apps.core.models import Driver, Team, Track, Car, LiveSession, LiveTelemetryPoint, LiveLap
from apps.core.services.lap_sim import simulate_lap, build_speed_polyline, build_ticks_y, build_ticks_x
from apps.users.forms import CustomUserCreationForm


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


@require_http_methods(["GET","POST"])
def live_telemetry(request):
    form = LiveSetupForm(request.POST or None)
    session = None
    last_lap = None
    poly = ""
    y_ticks = []
    x_ticks = []

    if request.method == "POST" and form.is_valid():
        car = form.cleaned_data["car"]
        driver = form.cleaned_data["driver"]
        track = form.cleaned_data["track"]

        session = LiveSession.objects.filter(finished_at__isnull=True).order_by("-id").first()
        if session:
            session.car = car; session.driver = driver; session.track = track; session.save()

    session = session or LiveSession.objects.order_by("-id").first()
    if session:
        last_lap = session.laps.order_by("-lap_number").first()
        if last_lap:
            pts = list(last_lap.points.order_by("t_ms").values_list("t_ms","speed_kmh"))
            if pts:
                total_ms = max(1, pts[-1][0])
                points = []
                for i,(t_ms, v) in enumerate(pts):
                    points.append((t_ms/1000.0, v))
                poly = build_speed_polyline(points, w=1000, h=260, pad=40, y_min=40, y_max=360)
                y_ticks = build_ticks_y(h=260, pad=40, y_min=40, y_max=360, step=40)
                x_ticks = build_ticks_x(total_sec=total_ms/1000.0, w=1000, pad=40, parts=5)

    return render(request, "core/pages/live_latest_lap.html", {
        "form": form,
        "session": session,
        "lap": last_lap,
        "poly": poly,
        "y_ticks": y_ticks,
        "x_ticks": x_ticks,
    })

def live_lap_export(request, lap_id: int):
    lap = LiveLap.objects.select_related("session").get(pk=lap_id)
    pts = list(lap.points.order_by("t_ms")
               .values_list("t_ms", "speed_kmh", "throttle", "brake"))
    if not pts:
        raise Http404("No data")

    t0 = pts[0][0]
    T  = [(t - t0)/1000.0 for (t, *_rest) in pts]
    V  = [v or 0.0 for (_t, v, *_r) in pts]
    TH = [th or 0.0 for (_t, _v, th, _b) in pts]
    BR = [b or 0.0 for (_t, _v, _th, b) in pts]

    mem = BytesIO()
    with zipfile.ZipFile(mem, "w", zipfile.ZIP_DEFLATED) as zf:
        meta = {
            "lap_id": lap.id,
            "lap_number": lap.lap_number,
            "lap_time_ms": lap.lap_time_ms,
            "sector1_ms": lap.sector1_ms,
            "sector2_ms": lap.sector2_ms,
            "sector3_ms": lap.sector3_ms,
            "car_label": lap.session.car_label,
            "driver_label": lap.session.driver_label,
            "track_label": lap.session.track_label,
        }
        zf.writestr("meta.json", json.dumps(meta, ensure_ascii=False, indent=2))

        csv_buf = BytesIO()
        writer = csv.writer(csv_buf)
        writer.writerow(["t_sec", "speed_kmh", "throttle_pct", "brake_pct"])
        for i in range(len(T)):
            writer.writerow([f"{T[i]:.3f}", V[i], f"{TH[i]:.1f}", f"{BR[i]:.1f}"])
        zf.writestr("telemetry.csv", csv_buf.getvalue().decode("utf-8"))

        fig1 = plt.figure()
        plt.plot(T, V)
        plt.xlabel("Time (s)"); plt.ylabel("km/h"); plt.title("Speed")
        buf1 = BytesIO(); fig1.savefig(buf1, format="png", dpi=160, bbox_inches="tight")
        plt.close(fig1)
        zf.writestr("speed.png", buf1.getvalue())

        fig2 = plt.figure()
        plt.plot(T, TH, label="Throttle %")
        plt.plot(T, BR, label="Brake %")
        plt.xlabel("Time (s)"); plt.ylabel("%"); plt.title("Throttle / Brake")
        plt.legend()
        buf2 = BytesIO(); fig2.savefig(buf2, format="png", dpi=160, bbox_inches="tight")
        plt.close(fig2)
        zf.writestr("throttle_brake.png", buf2.getvalue())

    mem.seek(0)
    filename = f"lap_{lap.lap_number or lap.id}.zip"
    resp = FileResponse(mem, as_attachment=True, filename=filename, content_type="application/zip")
    return resp

def live_latest_lap_page(request):
    bind_form = LiveBindForm(request.POST or None)

    sess = LiveSession.objects.order_by("-id").first()
    if not sess:
        return render(request, "core/pages/live_empty.html")

    if request.method == "POST" and bind_form.is_valid():
        car    = bind_form.cleaned_data["car"]
        driver = bind_form.cleaned_data["driver"]
        track  = bind_form.cleaned_data["track"]
        if car:    sess.car_label = getattr(car, "name", str(car))
        if driver: sess.driver_label = getattr(driver, "name", str(driver))
        if track:  sess.track_label = getattr(track, "name", str(track))
        sess.save()
        return redirect("live_latest_lap")  # оновимо сторінку

    lap = (LiveLap.objects
           .filter(session=sess, lap_time_ms__isnull=False, points__isnull=False)
           .order_by("-id").first())
    if not lap:
        return render(request, "core/pages/live_empty.html")

    return render(request, "core/pages/live_latest_lap.html", {
        "lap_id": lap.id,
        "bind_form": bind_form,
        "session": sess,
    })




def live_latest_lap_id(request):
    sess = LiveSession.objects.order_by("-id").first()
    if not sess:
        return JsonResponse({"lap_id": None})
    lap = (LiveLap.objects
           .filter(session=sess, lap_time_ms__isnull=False, points__isnull=False)
           .order_by("-id").first())
    return JsonResponse({"lap_id": lap.id if lap else None})


def live_lap_telemetry(request, lap_id: int):
    lap = LiveLap.objects.select_related("session").get(pk=lap_id)
    pts = (lap.points
               .order_by("t_ms")
               .values_list("t_ms", "speed_kmh", "throttle", "brake"))

    if not pts:
        return JsonResponse({"t": [], "speed": [], "thr": [], "brk": [], "meta": {}})

    t0 = pts[0][0]
    t, speed, thr, brk = [], [], [], []
    for t_ms, v, th, br in pts:
        t.append(round((t_ms - t0) / 1000.0, 3))
        speed.append(v or 0.0)
        thr.append(th or 0.0)
        brk.append(br or 0.0)

    meta = {
        "lap_number": lap.lap_number,
        "lap_time_ms": lap.lap_time_ms,
        "s1_ms": lap.sector1_ms,
        "s2_ms": lap.sector2_ms,
        "s3_ms": lap.sector3_ms,
        "car_label": getattr(lap.session, "car_label", "—"),
        "driver_label": getattr(lap.session, "driver_label", "—"),
        "track_label": getattr(lap.session, "track_label", "—"),
    }
    return JsonResponse({"t": t, "speed": speed, "thr": thr, "brk": brk, "meta": meta})

class RegisterView(generic.CreateView):
    form_class = CustomUserCreationForm
    template_name = "core/pages/register.html"
    success_url = reverse_lazy("login")




class CustomLoginView(LoginView):
    template_name = "core/pages/login.html"

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
        
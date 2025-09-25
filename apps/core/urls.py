from django.urls import path
from apps.core.views import welcome_view, teams, drivers, DriverDetailUpdateView, TeamDetailUpdateView, \
    tracks, TrackDetailUpdateView, cars, CarDetailUpdateView, lap_telemetry, live_telemetry, live_latest_lap_page, \
    live_lap_telemetry, live_latest_lap_id, live_lap_export, CustomLoginView, RegisterView

urlpatterns=[
    path('',welcome_view, name='welcome'),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("register/", RegisterView.as_view(), name="register"),
    path("live/latest/", live_latest_lap_page, name="live_latest_lap"),
    path("live/laps/<int:lap_id>/telemetry.json", live_lap_telemetry, name="live_lap_telemetry"),

    path("live/latest/id.json", live_latest_lap_id, name="live_latest_lap_id"),
    path("live/laps/<int:lap_id>/export.zip", live_lap_export, name="live_lap_export"),
    path("live-telemetry/", live_telemetry, name="live_telemetry"),
    path("lap-telemetry/", lap_telemetry, name="lap_telemetry"),
    path('drivers/',drivers, name='drivers'),
    path('teams/',teams, name='teams'),
    path("cars/", cars, name="cars"),
    path("cars/<int:pk>/", CarDetailUpdateView.as_view(), name="car_detail"),
    path("tracks/", tracks, name="tracks"),
    path("tracks/<int:pk>/", TrackDetailUpdateView.as_view(), name="track_detail"),
    path("drivers/<int:pk>/", DriverDetailUpdateView.as_view(), name="driver_detail"),
    path("teams/<int:pk>/", TeamDetailUpdateView.as_view(), name="team_detail"),
]
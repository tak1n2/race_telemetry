from django.urls import path
from apps.core.views import about_view, welcome_view, teams, drivers, DriverDetailUpdateView, TeamDetailUpdateView, \
    tracks, TrackDetailUpdateView, cars, CarDetailUpdateView, lap_telemetry

urlpatterns=[
    path('',welcome_view, name='welcome'),

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
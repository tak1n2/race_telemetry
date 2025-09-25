from django.contrib.auth.views import LogoutView
from django.urls import path
from django.views.generic import TemplateView

from apps.core.views import welcome_view, teams, drivers, DriverDetailUpdateView, TeamDetailUpdateView, \
    tracks, TrackDetailUpdateView, cars, CarDetailUpdateView, lap_telemetry, live_telemetry, live_latest_lap_page, \
    live_lap_telemetry, live_latest_lap_id, live_lap_export, CustomLoginView, RegisterView, ProfileView, logout_view

urlpatterns=[
    path('', welcome_view, name='welcome'),

    # Аутентифікація
    path('users/login/', CustomLoginView.as_view(), name='login'),
    path('users/register/', RegisterView.as_view(), name='register'),
    path('users/profile/', ProfileView.as_view(), name='profile'),
    path('users/logout/', logout_view, name='logout'),
    path('users/logged-out/', TemplateView.as_view(template_name="core/pages/logged_out.html"), name='logged_out'),


    # Live telemetry
    path("live/latest/", live_latest_lap_page, name="live_latest_lap"),
    path("live/laps/<int:lap_id>/telemetry.json", live_lap_telemetry, name="live_lap_telemetry"),
    path("live/latest/id.json", live_latest_lap_id, name="live_latest_lap_id"),
    path("live/laps/<int:lap_id>/export.zip", live_lap_export, name="live_lap_export"),
    path("live-telemetry/", live_telemetry, name="live_telemetry"),
    path("lap-telemetry/", lap_telemetry, name="lap_telemetry"),

    # Дані
    path('drivers/', drivers, name='drivers'),
    path("drivers/<int:pk>/", DriverDetailUpdateView.as_view(), name="driver_detail"),

    path('teams/', teams, name='teams'),
    path("teams/<int:pk>/", TeamDetailUpdateView.as_view(), name="team_detail"),

    path("cars/", cars, name="cars"),
    path("cars/<int:pk>/", CarDetailUpdateView.as_view(), name="car_detail"),

    path("tracks/", tracks, name="tracks"),
    path("tracks/<int:pk>/", TrackDetailUpdateView.as_view(), name="track_detail"),
]
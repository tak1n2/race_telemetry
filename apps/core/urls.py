from django.urls import path
from apps.core.views import about_view, welcome_view, teams, drivers, DriverDetailUpdateView, TeamDetailUpdateView

urlpatterns=[
    path('',welcome_view, name='welcome'),
    path('drivers/',drivers, name='drivers'),
    path('teams/',teams, name='teams'),
    path('about/',about_view, name='about'),
    path('tack_selection/',about_view, name='track_selection'),
    path("drivers/<int:pk>/", DriverDetailUpdateView.as_view(), name="driver_detail"),
    path("teams/<int:pk>/", TeamDetailUpdateView.as_view(), name="team_detail"),
]
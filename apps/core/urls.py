from django.urls import path
from apps.core.views import about_view, welcome_view

urlpatterns=[
    path('',welcome_view, name='welcome'),
    path('drivers/',drivers_view, name='drivers'),
    path('tack_selection/',about_view, name='track_selection'),
]
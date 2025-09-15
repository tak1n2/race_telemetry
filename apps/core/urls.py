from django.urls import path
from apps.core.views import about_view, welcome_view

urlpatterns=[
    path('',welcome_view, name='welcome'),
    path('',about_view, name='about'),
]
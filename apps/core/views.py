from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.decorators.http import require_http_methods

from apps.core.forms import TeamForm, DriverForm
from apps.core.models import Driver, Team


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
        
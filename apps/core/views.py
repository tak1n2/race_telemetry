from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from apps.core.models import Driver, Team


# Create your views here.
def about_view(request):
   return render(request, 'about.html')

def welcome_view(request):
    return render(request,'core/pages/welcome.html')

@require_http_methods(["GET","POST"])
def drivers(request):
    #POST
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        number = request.POST.get("number")
        country = request.POST.get("country")
        team_id = request.POST.get("team")
        #
        Driver.objects.create(
            first_name = first_name,
            last_name = last_name,
            number = number,
            country = country,
            team=Team.objects.get(id=team_id)
        )
        return redirect("drivers")
    #GET
    context = {
        "driver_list": Driver.objects.all(),
        "teams": Team.objects.all(),
    }
    return render(request, "core/pages/drivers.html", context)

@require_http_methods(["GET","POST"])
def teams(request):
    #POST
    if request.method == "POST":
        name = request.POST.get("name")
        country = request.POST.get("country")
        #
        Team.objects.create(
            name = name,
            country = country
        )
        return redirect("teams")
    #GET
    context = {
        "team_list": Team.objects.all()
    }
    return render(request, "core/pages/teams.html", context)
        
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def about_view(request):
   return render(request, 'about.html')

def welcome_view(request):
    return render(request,'core/pages/welcome.html')

@require_http_methods(["GET","POST"])
def drivers(request):
    #POST
    if request.method == "POST":
        first_name = request.POST.get("first_name");
        last_name = request.POST.get("last_name");
        number = request.POST.get("number");
        country = request.POST.get("country");
        team = request.POST.get("team");
        #
        Drivers.objects.create(
            first_name = first_name,
            last_name = last_name,
            number = number,
            country = country,
            team = team
        )
        return redirect("drivers")
    #GET
    context = {
        "driver_list": Driver.object.all(),
        "team": Team,
    }
    return render(request, "core/pages/drivers.html", context)
        
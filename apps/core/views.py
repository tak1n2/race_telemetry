from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def about_view(request):
    print(request)
    #return HttpResponse("Hello, world. You're at the polls page.")
    return HttpResponse(request,'about.html')

def welcome_view(request):
    return render(request,'core/pages/welcome.html')
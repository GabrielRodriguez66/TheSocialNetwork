from django.shortcuts import render
from django.views import generic
from .models import User

# Create your views here.


def register_form(request):
    return render(request, 'social/register.html')


def register(request):
    username = request.POST["username"]
    password = request.POST["password"]

    if User.objects.filter(username=username).count() != 0:
        return render(request, "social/register.html",
        {"error_message": "Username already taken."})
    if username == "":
        return render(request, "social/register.html",
                      {"error_message": "Username cannot be empty."})
    if len(password) < 8 or len(password) > 30:
        return render(request, "social/register.html",
                      {"error_message": "Password must be 8-30 characters long."})
    User.objects.create(username=username, password=password)








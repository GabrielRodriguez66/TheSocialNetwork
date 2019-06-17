from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import ListView
from django.shortcuts import render
from .models import User


class MyFriendsView(ListView):
    template_name = 'social/my_friends.html'
    context_object_name = 'my_friends_list'

    def get_queryset(self):
        """
            Excludes any questions that aren't published yet.
        """
        return User.objects.first().friends.all()


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


def unfriend(request, friend_pk):
    get_object_or_404(User, pk=User.objects.first().id).friends.remove(friend_pk)
    return HttpResponseRedirect(reverse('social:my_friends'))

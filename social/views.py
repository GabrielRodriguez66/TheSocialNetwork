from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render, reverse
from django.views.generic import ListView

from social.admin import SocialNetworkBackend
from .forms import SearchForm
from .models import SocialNetworkUser


class MyFriendsView(ListView):
    template_name = 'social/my_friends.html'
    context_object_name = 'my_friends_list'

    def get_queryset(self):
        """
            Excludes any questions that aren't published yet.
        """
        return SocialNetworkUser.objects.first().friends.all()


def register_form(request):
    return render(request, 'social/register.html')


def login(request, username, password):
    backend = SocialNetworkBackend()
    user = backend.authenticate(username, password)
    if user:
        pass  # Authenticated
    else:
        pass  # Not authenticated


def register(request):
    username = request.POST["username"]
    password = request.POST["password"]

    if SocialNetworkUser.objects.filter(username=username).count() != 0:
        return render(request, "social/register.html",
        {"error_message": "Username already taken."})
    if username == "":
        return render(request, "social/register.html",
                      {"error_message": "Username cannot be empty."})
    if len(password) < 8 or len(password) > 30:
        return render(request, "social/register.html",
                      {"error_message": "Password must be 8-30 characters long."})
    SocialNetworkUser.objects.create(username=username, password=password)


def unfriend(request, friend_pk):
    get_object_or_404(SocialNetworkUser, pk=SocialNetworkUser.objects.first().id).friends.remove(friend_pk)
    return HttpResponseRedirect(reverse('social:my_friends'))


def search(request):
    users = SocialNetworkUser.objects.all()
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            if request.POST["username"] != '':
                users = SocialNetworkUser.objects.filter(username=request.POST["username"])
    else:
        form = SearchForm()
    context = {
        'users': users,
        'form': form
    }

    return render(request, 'social/search.html', context)

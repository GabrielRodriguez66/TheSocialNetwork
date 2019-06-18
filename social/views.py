import json

import django
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.shortcuts import render, reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView

from social.admin import SocialNetworkBackend
from social.forms import RegisterForm, LoginForm
from .forms import SearchForm, ShoutForm
from .models import SocialNetworkUser, Shout


@never_cache
@require_http_methods(["POST"])
def asocia_usuario(request):
    content_type = "application/json"
    response = HttpResponse(content_type=content_type)
    try:
        User = get_user_model()
        usuario_existente = User.objects.get(username__iexact=request.POST.get('username', ""))
        response.write(json.dumps({"resultado": "Este usuario ya existe en el sistema.",
                                   "nombre_completo": usuario_existente.get_full_name(),
                                   "nombre_usuario": usuario_existente.username,
                                   "email": usuario_existente.email, }))
    except ObjectDoesNotExist:
        response.write(json.dumps(SocialNetworkBackend().get_user_info(request.POST.get('username', ""))))
    return response


class MyFriendsView(ListView):
    template_name = 'social/my_friends.html'
    context_object_name = 'my_friends_list'

    def get_queryset(self):
        """
            Excludes any questions that aren't published yet.
        """
        return self.request.user.socialnetworkuser.friends.all()

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(MyFriendsView, self).dispatch(request, *args, **kwargs)


def logout_view(request):
    django.contrib.auth.logout(request)
    return HttpResponseRedirect(settings.LOGIN_URL)


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            backend = SocialNetworkBackend()
            user = backend.authenticate(request, form.cleaned_data['username'], form.cleaned_data['password'],
                                        must_exist=True)
            if user:
                django.contrib.auth.login(request, user)
                return HttpResponseRedirect(reverse("social:timeline"), request)
                # Authenticated
            else:
                # Not authenticated
                return render(request, "social/login.html",
                              context={'form': LoginForm(), 'error_message': "Username or password is incorrect"})
    elif request.method == "GET":
        return render(request, "social/login.html", context={'form': LoginForm()})


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            auth_only_backend = SocialNetworkBackend()
            authenticated = auth_only_backend.authenticate(request, form.cleaned_data['buscador_de_usuario'],
                                                           form.cleaned_data['password'], must_exist=False)
            if authenticated:
                if not SocialNetworkUser.objects.filter(usuario__username=authenticated.username).exists():
                    user_info = auth_only_backend.get_user_info(form.cleaned_data['buscador_de_usuario'])
                    auth_only_backend.create_user(authenticated, user_info)
                    return HttpResponseRedirect(reverse("social:timeline"))
                else:
                    return render(request, "social/register.html", context={'form': form,
                                                                            'error_message': 'User already exists'})
            else:
                return render(request, "social/register.html", context={'form': form,
                                                                'error_message': 'Username or Password is incorrect.'})
        else:
            return render(request, "social/register.html", context={'form': form})
    elif request.method == 'GET':
        return render(request, "social/register.html", context={'form': RegisterForm()})
    else:
        return Http404()


@login_required
def unfriend(request, friend_pk):
    get_object_or_404(SocialNetworkUser, pk=request.user).friends.remove(friend_pk)
    return HttpResponseRedirect(reverse('social:my_friends'))


@login_required
def search(request):
    users = SocialNetworkUser.objects.exclude(usuario=request.user)
    auth = request.user.socialnetworkuser
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            if request.POST["username"] != '':
                users = SocialNetworkUser.objects.filter(usuario__username__contains=request.POST["username"])
    else:
        form = SearchForm()
    context = {
        'users': [(user, auth in user.friends.all()) for user in users],
        'form': form
    }

    return render(request, 'social/search.html', context)


def search_view_unfriend(request, friend_pk):
    get_object_or_404(SocialNetworkUser, pk=request.user.socialnetworkuser.id).friends.remove(friend_pk)
    return HttpResponseRedirect(reverse('social:search'))


@login_required
def timeline(request):
    if request.method == 'POST':
        form = ShoutForm(request.POST or None)
        if form.is_valid():
            Shout.objects.create(shout_text=request.POST["shout_text"], author= request.user.socialnetworkuser,
                                 pub_date=timezone.now())
            return HttpResponseRedirect(reverse("social:timeline"))
    else:
        form = ShoutForm()
    shouts = Shout.objects.order_by('-pub_date')
    return render(request, 'social/timeline.html', {'shouts': shouts, 'forms': form,})


def home(request):
    return HttpResponseRedirect(reverse("social:timeline"))
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
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods

from social.admin import SocialNetworkBackend
from social.forms import RegisterForm, LoginForm
from .forms import SearchForm, ShoutForm
from .models import SocialNetworkUser, Message, FriendRequested


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


@login_required
def friends_view(request, friend_pk=None, view=None):
    form = ShoutForm()
    friends = request.user.socialnetworkuser.friends.all()
    return render(request, 'social/my_friends.html', {'my_friends_list': friends, 'form': form, })


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
def unfriend(request, friend_pk, view):
    get_object_or_404(SocialNetworkUser, pk=request.user.socialnetworkuser.id).friends.remove(friend_pk)
    return HttpResponseRedirect(reverse('social:'+view))


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
        'form': form,
        'chat': ShoutForm(),
        'auth_user': auth
    }
    return render(request, 'social/search.html', context)


def friend_request(request, friend_pk):
    req = FriendRequested.objects.create(remitente=request.user.socialnetworkuser, destinatario_id=friend_pk)
    request.user.socialnetworkuser.requesting.add(req)
    return HttpResponseRedirect(reverse('social:search'))


def respond_request(request, request_pk, accepted):
    req = get_object_or_404(FriendRequested, pk=request_pk)
    dest = req.destinatario
    rem = req.remitente
    if accepted:
        dest.friends.add(rem)
    # rem.requesting.remove(req)
    FriendRequested.objects.filter(pk=request_pk).delete()
    return HttpResponseRedirect(reverse('social:timeline'))


def search_view_unfriend(request, friend_pk):
    get_object_or_404(SocialNetworkUser, pk=SocialNetworkUser.objects.first().id).friends.remove(friend_pk)
    return HttpResponseRedirect(reverse('social:search'))


@login_required
def timeline(request):
    if request.method == 'POST':
        form = ShoutForm(request.POST or None)
        if form.is_valid():
            #get all friends
            recipients = request.user.socialnetworkuser.friends.all()
            message = Message.objects.create(text=request.POST["text"], author=request.user.socialnetworkuser,
                                           pub_date=timezone.now())
            message.recipients.add(request.user.socialnetworkuser)
            for recipient in recipients:
                message.recipients.add(recipient)
            return HttpResponseRedirect(reverse("social:timeline"))
    else:
        form = ShoutForm()
    messages = Message.objects.filter(recipients=request.user.socialnetworkuser).order_by('-pub_date')
    friend_requests = FriendRequested.objects.filter(destinatario=request.user.socialnetworkuser.usuario_id)
    return render(request, 'social/timeline.html', {'shouts': messages, 'forms': form, 'hasRequests': friend_requests,})


def home(request):
    return HttpResponseRedirect(reverse("social:timeline"))


@login_required
def chat_manager(request, friend_pk, view):
    form = ShoutForm(request.POST or None)
    if form.is_valid():
        message = Message.objects.create(text=request.POST["text"], author=request.user.socialnetworkuser,
                                         pub_date=timezone.now())
        recipient = get_object_or_404(SocialNetworkUser, pk=friend_pk)
        message.recipients.add(request.user.socialnetworkuser)
        message.recipients.add(recipient)
        return HttpResponseRedirect(reverse("social:"+view))

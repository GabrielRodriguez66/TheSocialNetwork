import base64
import json

import django
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.shortcuts import render, reverse
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods

from social.admin import SocialNetworkBackend
from social.forms import RegisterForm, LoginForm, ProfileHandle, ProfilePic
from .forms import SearchForm, ShoutForm
from .models import SocialNetworkUser, Message, FriendRequested, UploadedPic
from social.forms import RegisterForm, LoginForm, ChatForm, SearchForm, ShoutForm, ReceiverForm
from .models import SocialNetworkUser, Message, FriendRequested, Chat


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
def friends_view(request):
    form = ChatForm()
    friends = request.user.socialnetworkuser.friends.all()
    return render(request, 'social/my_friends.html', {'my_friends_list': friends, 'form': form, 'shouts':
        Message.objects.filter(recipients=request.user.socialnetworkuser).order_by('-pub_date') })


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
                users = SocialNetworkUser.objects.filter(usuario__username__iexact=request.POST["username"])
                if not users.first():
                    users = SocialNetworkUser.objects.filter(
                        Q(usuario__username__trigram_similar=request.POST["username"])
                        | Q(usuario__username__icontains=request.POST["username"])) \
                        .exclude(usuario=request.user)

    else:
        form = SearchForm()
    context = {
        'users': [(user, auth in user.friends.all()) for user in users],
        'form': form,
        'chat': ChatForm(),
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
    if accepted == 1:
        dest.friends.add(rem)
    rem.requesting.remove(req)
    FriendRequested.objects.filter(pk=request_pk).delete()
    return HttpResponseRedirect(reverse('social:timeline'))


def search_view_unfriend(request, friend_pk):
    get_object_or_404(SocialNetworkUser, pk=SocialNetworkUser.objects.first().id).friends.remove(friend_pk)
    return HttpResponseRedirect(reverse('social:search'))


@login_required
def timeline(request):

    # TODO: Fix filters !!!

    messages = Message.objects.filter(Q(author=request.user.socialnetworkuser) | Q(
        recipients=request.user.socialnetworkuser)).order_by('-pub_date')
    senderform = SearchForm(request.POST)
    receiverform = ReceiverForm(request.POST)
    if request.method == 'POST':
        form = ShoutForm(request.POST or None)
        if form.is_valid():
            recipients = request.user.socialnetworkuser.friends.all()
            message = Message.objects.create(text=request.POST["text"], author=request.user.socialnetworkuser,
                                             pub_date=timezone.now())
            for recipient in recipients:
                message.recipients.add(recipient)
                return HttpResponseRedirect(reverse("social:timeline"))
        if request.POST['filter'] == '1':
            if senderform.is_valid():
                if request.POST["username"] != '':
                    messages = Message.objects.filter(author__usuario__username__contains=request.POST["username"]).order_by('-pub_date')
        if request.POST['filter'] == '2':
            if receiverform.is_valid():
                if request.POST["username"] != '':
                    user = SocialNetworkUser.objects.filter(usuario__username__contains=request.POST["username"])
                    messages = Message.objects.filter(recipients=user, allowed=True).order_by('-pub_date')
        if request.POST['filter'] == '3':
            messages = Message.objects.filter(Q(author=request.user.socialnetworkuser) | Q(
                recipients__in=[request.user.socialnetworkuser]), pub_date__day=timezone.now().day).order_by('-pub_date')
        if request.POST['filter'] == '4':
            messages = Message.objects.filter(recipients__in=[request.user.socialnetworkuser],
                                              author=request.user.socialnetworkuser, chat=None).order_by('-pub_date')
        if request.POST['filter'] == '5':
            messages = Message.objects.filter(Q(author=request.user.socialnetworkuser) | Q(
                recipients__in=[request.user.socialnetworkuser])).order_by('-pub_date')
    else:
        form = ShoutForm()
    friend_requests = FriendRequested.objects.filter(destinatario=request.user.socialnetworkuser.usuario_id)
    return render(request, 'social/timeline.html', {'shouts': messages,
                                                    'forms': form,
                                                    'friend_requests': friend_requests,
                                                    'senderform': senderform,
                                                    'receiverform': receiverform,
                                                    })


@login_required
def home(request):
    return HttpResponseRedirect(reverse("social:timeline"))


@login_required
def chat_manager(request, friend_pk, view=None, chat_pk=None):
    form = ChatForm(request.POST or None) if chat_pk is not None else ShoutForm(request.POST or None)
    if form.is_valid():
        message = Message.objects.create(text=request.POST["text"], author=request.user.socialnetworkuser,
                                         pub_date=timezone.now())
        recipient = get_object_or_404(SocialNetworkUser, pk=friend_pk)
        message.recipients.add(recipient)
        if chat_pk is not None:
            chat = Chat.objects.create(creation_date=timezone.now()) if chat_pk == 0 else get_object_or_404(Chat,
                                                                                                            pk=chat_pk)
            message.chat = chat
            message.save()
            creation_date = chat.creation_date
            messages = [message] if chat_pk == 0 else chat.message_set.order_by('-pub_date')
            friend = message.recipients.first()
            return render(request, 'social/chat.html',
                          {"chat_id": chat.id, "friend": friend, "date": creation_date, 'chat_messages': messages,
                           'chat_form': ChatForm()})
    return HttpResponseRedirect(reverse("social:"+view))


@login_required
def open_chat_view(request, message_id):
    message = get_object_or_404(Message, pk=message_id)
    chat = message.chat
    messages = chat.message_set.order_by('-pub_date')
    creation_date = chat.creation_date
    friend = message.recipients.first()
    return render(request, 'social/chat.html', {"chat_id": chat.id, "friend": friend, "date": creation_date, 'chat_messages': messages,
                                                'chat_form': ChatForm()})


@login_required
def profile(request):
    if request.user.socialnetworkuser.has_pic:
        data = UploadedPic.objects.get(user=request.user.socialnetworkuser)
        pic_data = str(bytes(data.pic)).split("'")[1]
        pic = "data:image/jpeg;base64, " + str(pic_data).split("'")[0]
    else:
        pic = "/static/social/images/default.jpg"
    if request.method == "POST":
        for user in SocialNetworkUser.objects.all():
            if user.handle == request.POST["handle"]:
                return render(request, 'social/profile.html',
                              {"error_message": "Handle is taken", "handle_form": ProfileHandle(),
                               "pic_url": pic, "pic_form": ProfilePic()})
        request.user.socialnetworkuser.handle = request.POST['handle']
        request.user.socialnetworkuser.save()
        return render(request, 'social/profile.html', {"handle_form": ProfileHandle(),
                                                       "pic_url": pic, "pic_form": ProfilePic()})
    else:
        return render(request, 'social/profile.html', {"handle_form": ProfileHandle(),
                                                       "pic_url": pic,
                                                       "pic_form": ProfilePic()})


@login_required
def profile_pic(request):
    pic = request.FILES["pic"]
    upload(request, pic)
    request.user.socialnetworkuser.has_pic = True
    request.user.socialnetworkuser.save()
    return HttpResponseRedirect(reverse("social:profile"))


def upload(request, obj):
    exists = UploadedPic.objects.filter(user=request.user.socialnetworkuser).count()
    try:
        if exists == 0:
            pdf = UploadedPic()
            file = obj
            file_data = file.read()
            pdf.pic = base64.b64encode(file_data)
            pdf.tipo_mime = "image/jpeg"
            pdf.user = request.user.socialnetworkuser
            pdf.save()
            obj.archivo = pdf
        else:
            pdf = UploadedPic.objects.get(user=request.user.socialnetworkuser)
            file_data = obj.read()
            pdf.pic = base64.b64encode(file_data)
            pdf.save()
            obj.archivo = pdf
    except KeyError:
        pass


def delete_pic(request):
    user = request.user.socialnetworkuser
    if user.has_pic:
        UploadedPic.objects.get(user=user).delete()
        user.has_pic = False
        user.save()
        return HttpResponseRedirect(reverse("social:profile"))
    else:
        return HttpResponseRedirect(reverse("social:profile"))


import base64
import json

import django
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.postgres.search import TrigramSimilarity
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, Subquery
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.shortcuts import render, reverse
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods

from social.admin import SocialNetworkBackend
from social.forms import ProfileHandle, ProfilePic
from social.forms import RegisterForm, LoginForm, ChatForm, SearchForm, ShoutForm, ReceiverForm
from .models import PENDING_STATUS, ACCEPTED_STATUS, \
    REJECTED_STATUS, IGNORED_STATUS, CANCELED_STATUS, REQUEST_STATUS_CHOICES
from .models import Recibido
from .models import SocialNetworkUser, Message, FriendRequested, Chat
from .models import UploadedPic


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
                    user = auth_only_backend.create_user(authenticated, user_info)
                    django.contrib.auth.login(request, user)
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
            clean_search_name = form.cleaned_data["username"]
            if clean_search_name != '':
                users = SocialNetworkUser.objects.annotate(
                    similarity=TrigramSimilarity('usuario__username', clean_search_name)).filter(
                    Q(usuario__username__icontains=clean_search_name) | Q(similarity__gt=0.5)).order_by('-similarity') \
                    .exclude(usuario=request.user)
    else:
        form = SearchForm()
    context = {
        'users': [(user, auth in user.friends.all(), FriendRequested.objects.filter(destinatario=user, remitente=auth,
                                                                    status=PENDING_STATUS).first()) for user in users],
        'form': form,
        'chat': ChatForm(),
        'auth_user': auth
    }
    return render(request, 'social/search.html', context)


def friend_request(request, friend_pk):
    if not FriendRequested.objects.filter(remitente=request.user.socialnetworkuser, destinatario_id=friend_pk,
                                          status=PENDING_STATUS).first():
        req = FriendRequested.objects.create(remitente=request.user.socialnetworkuser, destinatario_id=friend_pk)
        request.user.socialnetworkuser.requesting.add(req)
    return HttpResponseRedirect(reverse('social:search'))


def respond_request(request, request_pk, accepted):
    req = get_object_or_404(FriendRequested, pk=request_pk)
    dest = req.destinatario
    rem = req.remitente
    status_choices = dict(REQUEST_STATUS_CHOICES)
    if accepted == ACCEPTED_STATUS:
        dest.friends.add(rem)
        req.status = ACCEPTED_STATUS
        message = Message.objects.create(text=status_choices.get(ACCEPTED_STATUS), author=dest,
                                         pub_date=timezone.now(), chat=Chat.objects.create(creation_date=timezone.now()))
        Recibido.objects.create(message_id=message, user_id=rem)
    elif accepted == REJECTED_STATUS:
        req.status = REJECTED_STATUS
        message = Message.objects.create(text=status_choices.get(REJECTED_STATUS), author=dest,
                                         pub_date=timezone.now(), chat=Chat.objects.create(creation_date=timezone.now()))
        Recibido.objects.create(message_id=message, user_id=rem)
    elif accepted == IGNORED_STATUS:
        req.status = IGNORED_STATUS
    elif accepted == CANCELED_STATUS:
        req.status = CANCELED_STATUS
        req.save()
        return HttpResponseRedirect(reverse('social:search'))
    req.save()
    return HttpResponseRedirect(reverse('social:timeline'))


def search_view_unfriend(request, friend_pk):
    get_object_or_404(SocialNetworkUser, pk=request.user.socialnetworkuser.id).friends.remove(friend_pk)
    return HttpResponseRedirect(reverse('social:search'))


@login_required
def timeline(request):
    displayedMessages = Recibido.objects.filter(Q(user_id=request.user.socialnetworkuser) | Q(message_id__author=
                                                request.user.socialnetworkuser)).order_by('-message_id__pub_date')
    senderform = SearchForm(request.POST)
    receiverform = ReceiverForm(request.POST)
    if request.method == 'POST':
        form = ShoutForm(request.POST or None)
        if form.is_valid():
            recipients = request.user.socialnetworkuser.friends.all()
            message = Message.objects.create(text=request.POST["text"], author=request.user.socialnetworkuser,
                                             pub_date=timezone.now())
            for recipient in recipients:
                Recibido.objects.create(message_id=message, user_id=recipient)
                return HttpResponseRedirect(reverse("social:timeline"))
        if request.POST['filter'] == '1':
            if senderform.is_valid():
                username = senderform.cleaned_data["username"]
                if request.POST["username"] != '':
                    displayedMessages = Recibido.objects.filter(message_id__author__usuario__username__icontains=
                                                                username).order_by('-message_id__pub_date')
        if request.POST['filter'] == '2':
            if receiverform.is_valid():
                user = receiverform.cleaned_data["user"]
                if request.POST["user"] != '':
                    displayedMessages = Recibido.objects.filter(user_id__usuario__username__icontains=user).\
                                                                order_by('-message_id__pub_date')
        if request.POST['filter'] == '3':
            displayedMessages = Recibido.objects.filter((Q(user_id=request.user.socialnetworkuser) |
                                                         Q(message_id__author=request.user.socialnetworkuser)),
                                                        message_id__pub_date__day=timezone.now().day).\
                                                        order_by('-message_id__pub_date')

        if request.POST['filter'] == '4':
            displayedMessages = Recibido.objects.filter(Q(user_id=request.user.socialnetworkuser) |
                                                        Q(message_id__author=request.user.socialnetworkuser),
                                                        message_id__chat_id=None).order_by('-message_id__pub_date')
        if request.POST['filter'] == '5':
            displayedMessages = Recibido.objects.filter(Q(user_id=request.user.socialnetworkuser) |
                                                        Q(message_id__author=request.user.socialnetworkuser)).\
                                                        order_by('-message_id__pub_date')
    else:
        form = ShoutForm()
    friend_requests = FriendRequested.objects.filter(destinatario=request.user.socialnetworkuser, status=PENDING_STATUS)
    return render(request, 'social/timeline.html', {'messages_recibido': displayedMessages,
                                                    'forms': form,
                                                    'friend_requests': friend_requests,
                                                    'senderform': senderform,
                                                    'receiverform': receiverform,
                                                    'reject_text': dict(REQUEST_STATUS_CHOICES).get(REJECTED_STATUS),
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
        Recibido.objects.create(message_id=message, user_id=recipient)
        if chat_pk is not None:
            chat = Chat.objects.create(creation_date=timezone.now()) if chat_pk == 0 else get_object_or_404(Chat,
                                                                                                            pk=chat_pk)
            message.chat = chat
            message.save()
            creation_date, messages = chat.creation_date, chat.message_set
            recibido_messages = Recibido.objects.filter(message_id__in=Subquery(messages.values('id'))). \
                values_list('message_id__text', 'message_id__author__usuario__first_name',
                            'user_id__usuario__first_name',
                            'message_id__pub_date').order_by('-message_id__pub_date')
            return render(request, 'social/chat.html', {"friend_pk": friend_pk, "chat_id": chat.id, "date": creation_date,
                                                     "recibido_messages": recibido_messages, 'chat_form': ChatForm()})
    return HttpResponseRedirect(reverse("social:"+view))


@login_required
def open_chat_view(request, message_id):
    message = get_object_or_404(Message, pk=message_id)
    chat = message.chat
    messages = chat.message_set.order_by('-pub_date')
    creation_date = chat.creation_date
    recibido_messages = Recibido.objects.filter(message_id__in=Subquery(messages.values('id'))). \
        values_list('message_id__text', 'message_id__author__usuario__first_name',
                    'user_id__usuario__first_name',
                    'message_id__pub_date').order_by('-message_id__pub_date')

    friend_pk = message.recipients.first().id if message.author.usuario == request.user else message.author.id
    return render(request, 'social/chat.html', {"friend_pk": friend_pk, "chat_id": chat.id, "recibido_messages":
                                                recibido_messages, "date": creation_date, 'chat_form': ChatForm()})


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
            img = UploadedPic()
            file = obj
            file_data = file.read()
            img.pic = base64.b64encode(file_data)
            img.tipo_mime = "image/jpeg"
            img.user = request.user.socialnetworkuser
            img.save()
            obj.archivo = img
        else:
            img = UploadedPic.objects.get(user=request.user.socialnetworkuser)
            file_data = obj.read()
            img.pic = base64.b64encode(file_data)
            img.save()
            obj.archivo = img
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


@login_required
def friend_prof(request, friend_usuario_first_name):
    friend = request.user.socialnetworkuser.friends.get(usuario__first_name=friend_usuario_first_name)
    if friend.has_pic:
        data = UploadedPic.objects.get(user=friend)
        pic_data = str(bytes(data.pic)).split("'")[1]
        pic = "data:image/jpeg;base64, " + pic_data
    else:
        pic = "/static/social/images/default.jpg"
    return render(request, 'social/friend_profile.html', {"friend": friend, "pic_url": pic})


@login_required
def delete_prof(request):
    user = request.user.socialnetworkuser
    for friend in user.friends.all():
        user.friends.remove(friend)
    if user.has_pic:
        UploadedPic.objects.get(user=user).delete()
        user.has_pic = False
        user.save()
    django.contrib.auth.logout(request)
    User.objects.get(username=user.usuario.username).delete()
    return HttpResponseRedirect(settings.LOGIN_URL)



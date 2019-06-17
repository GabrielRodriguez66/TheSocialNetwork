from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import ListView

from .models import User


# Create your views here.
class MyFriendsView(ListView):
    template_name = 'social/my_friends.html'
    context_object_name = 'my_friends_list'

    def get_queryset(self):
        """
            Excludes any questions that aren't published yet.
        """
        return User.objects.first().friends.all()


def unfriend(request, friend_pk):
    get_object_or_404(User, pk=User.objects.first().id).friends.remove(friend_pk)
    return HttpResponseRedirect(reverse('social:my_friends'))

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

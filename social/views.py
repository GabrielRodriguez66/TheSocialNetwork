from django.utils import timezone
from django.shortcuts import render, reverse
from django.http import HttpResponse, HttpResponseRedirect
from .models import Shout, User
from .forms import ShoutForm

# Create your views here.
def timeline(request):
    if request.method == 'POST':
        form = ShoutForm(request.POST or None)
        if form.is_valid():
            Shout.objects.create(shout_text=request.POST["shout_text"], author=User.objects.first(), pub_date=timezone.now())
            return HttpResponseRedirect(reverse("social:timeline"))
    else:
        form = ShoutForm()
    shouts = Shout.objects.order_by('-pub_date')
    return render(request, 'social/timeline.html', {'shouts': shouts, 'forms': form,})






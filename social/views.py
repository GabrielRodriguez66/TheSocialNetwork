from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse
from .models import User
from .forms import SearchForm


def search(request):
    users = User.objects.all()
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            if request.POST["username"] != '':
                users = User.objects.filter(username=request.POST["username"])
    else:
        form = SearchForm()
    context = {
        'users': users,
        'form': form
    }

    return render(request, 'social/search.html', context)





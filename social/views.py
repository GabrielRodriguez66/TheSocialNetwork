from django.shortcuts import render

# Create your views here.
from social.admin import SocialNetworkBackend


def login(request):
    backend = SocialNetworkBackend()
    user = backend.authenticate(username, password)
    if user:
        # Authenticated
    else:
        # Not authenticated
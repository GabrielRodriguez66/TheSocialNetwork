from django.shortcuts import render

# Create your views here.
from social.admin import SocialNetworkBackend


def login(request, username, password):
    backend = SocialNetworkBackend()
    user = backend.authenticate(username, password)
    if user:
        pass  # Authenticated
    else:
        pass  # Not authenticated

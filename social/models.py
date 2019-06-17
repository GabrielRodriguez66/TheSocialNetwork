from django.conf import settings
from django.db import models


class SocialNetworkUser(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE())
    friends = models.ManyToManyField("self")

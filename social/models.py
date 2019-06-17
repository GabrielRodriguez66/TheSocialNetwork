from django.conf import settings
from django.db import models
from datetime import datetime


class SocialNetworkUser(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE())
    friends = models.ManyToManyField("self")


class Shout(models.Model):
    shout_text = models.TextField()
    pub_date = models.DateTimeField('date published', default=datetime.now())
    author = models.ForeignKey(SocialNetworkUser, on_delete=models.CASCADE)




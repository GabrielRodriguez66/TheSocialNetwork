from datetime import datetime

from django.conf import settings
from django.db import models


class FriendRequested(models.Model):
    remitente = models.ForeignKey('SocialNetworkUser', related_name='fuente', on_delete=models.CASCADE)
    destinatario = models.ForeignKey('SocialNetworkUser', related_name='receptor', on_delete=models.CASCADE)


class SocialNetworkUser(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    friends = models.ManyToManyField("self")
    requesting = models.ManyToManyField(FriendRequested)

    def __str__(self):
        return self.usuario.username


class Message(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField('date published', default=datetime.now())
    author = models.ForeignKey(SocialNetworkUser, on_delete=models.CASCADE)
    recipients = models.ManyToManyField(SocialNetworkUser, related_name="friend_list", blank=True)








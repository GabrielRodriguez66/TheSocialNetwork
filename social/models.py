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
    handle = models.CharField(max_length=10, default="")
    has_pic = models.BooleanField(default=False)

    def __str__(self):
        return self.usuario.username


class Chat(models.Model):
    creation_date = models.DateTimeField('date created')


class Message(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField('date published', default=datetime.now())
    author = models.ForeignKey(SocialNetworkUser, on_delete=models.CASCADE)
    recipients = models.ManyToManyField(SocialNetworkUser, through="Recibido", related_name="friend_list", blank=True)
    chat = models.ForeignKey(Chat, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.text


class UploadedPic(models.Model):
    pic = models.BinaryField(db_column='pic', blank=True, editable=True)
    tipo_mime = models.CharField(u"tipo MIME", max_length=255)
    user = models.CharField(max_length=255, default="")

    def __str__(self):
        return u"%s:%s" % (self.id, self.tipo_mime)



class Recibido(models.Model):
    message_id = models.ForeignKey(Message, on_delete=models.CASCADE)
    user_id = models.ForeignKey(SocialNetworkUser, on_delete=models.CASCADE)





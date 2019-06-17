from django.db import models
from django.core.validators import MinLengthValidator
from datetime import datetime


class User(models.Model):
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=30, validators=[MinLengthValidator(8, message="Password must be at least 8 characters long",)])
    friends = models.ManyToManyField("self")

    def __str__(self):
        return self.username

class Shout(models.Model):
    shout_text = models.TextField()
    pub_date = models.DateTimeField('date published', default=datetime.now())
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.id



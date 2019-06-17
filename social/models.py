from django.core.validators import MinLengthValidator
from django.db import models


class User(models.Model):
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=30, validators=[MinLengthValidator(8, message="Password must be at least 8 characters long",)])
    friends = models.ManyToManyField("self",  blank=True)

    def __str__(self):
        return self.username

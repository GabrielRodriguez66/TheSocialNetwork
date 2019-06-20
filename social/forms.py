from django import forms
from django.core.exceptions import ValidationError

from social.widgets import BuscadorDeUsuarioField


class ShoutForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea(attrs={'rows':4, 'cols': 60}), label='Shout', max_length=240, required=True)


class SearchForm(forms.Form):
    username = forms.CharField(label='Search', max_length=20, required=False)


class RegisterForm(forms.Form):
    template = "social/register.html"
    buscador_de_usuario = BuscadorDeUsuarioField(url="/social/asocia_usuario/",
                                                 timeout_milliseconds=8000,
                                                 label=u"Nombre de usuario", initial=u"Buscar...",
                                                 required=True)
    password = forms.CharField(label=u'Contraseña', widget=forms.PasswordInput, required=True, strip=True)

    # def clean_buscador_de_usuario(self):
    #     if self.data['username'] == "":
    #         raise ValidationError("Username cannot be empty.")
    #     else:
    #         self.clean_data['username'] = self.data['username']
    #
    def clean_password(self):
        password = self.data['password']
        if len(password) < 8 or len(password) > 30:
            raise ValidationError("Password must be 8-30 characters long.")
        else:
            self.cleaned_data['password'] = self.data['password']
        return password


class LoginForm(forms.Form):
    template = "social/login.html"
    username = forms.CharField(label=u"Nombre de usuario", strip=True)
    password = forms.CharField(label=u'Contraseña', widget=forms.PasswordInput, strip=True)

    def clean_password(self):
        password = self.data['password']
        if len(password) < 8 or len(password) > 30:
            raise ValidationError("Password must be 8-30 characters long.")
        else:
            self.cleaned_data['password'] = self.data['password']
        return password

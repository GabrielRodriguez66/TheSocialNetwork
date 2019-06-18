from django import forms
from django.core.exceptions import ValidationError

from social.widgets import BuscadorDeUsuarioField


class RegisterForm(forms.Form):
    template = "social/register.html"
    buscador_de_usuario = BuscadorDeUsuarioField(url="/social/asocia_usuario/",
                                                 timeout_milliseconds=8000,
                                                 label=u"Nombre de usuario a asociar", initial=u"Buscar...")
    password = forms.CharField(label=u'Contraseña', widget=forms.PasswordInput)

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

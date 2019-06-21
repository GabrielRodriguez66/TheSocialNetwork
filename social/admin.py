import ldap
from django.conf import settings
# Register your models here.
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User

#  Authentication Back-ends
from social.models import SocialNetworkUser


class TooManyEntries(Exception):
    pass


class InvalidServiceAccount(Exception):
    pass


class ActiveDirectoryBackend(ModelBackend):
    def __init__(self, *args, **kwargs):
        self.ad_url = settings.NOTARIAT_AD['ad_url']
        self.service_account_dn = settings.NOTARIAT_AD['service_account_dn']
        self.service_account_password = settings.NOTARIAT_AD['service_account_password']
        self.search_root = settings.NOTARIAT_AD['search_root']

    def authenticate(self, request, username=None, password=None, must_exist=True, **kwargs):
        if must_exist:
            user = self.get_user_by_username(username)
            # Funcionarios y jueces tienen que estar registrados para tener acceso
            if not user:
                return None
        else:
            user = None
        if not user:
            user = User(username=username, password='', is_active=True, is_staff=True, is_superuser=False)
        return user
        #Proceder a validar contraseña
        try:
            con = self.bind()
        except ldap.INVALID_CREDENTIALS:
            raise InvalidServiceAccount("Active Directory")

        ldap_search_results = con.search_s(self.search_root, ldap.SCOPE_SUBTREE, '(userPrincipalName=' + username + ')',
                                           ['distinguishedName', ])
        if 0 < len(ldap_search_results) < 2:
            dn = ldap_search_results[0][1]['distinguishedName'][0].decode("utf-8")
            con.unbind_s()
            try:
                con = self.bind(dn=dn, pwd=password)
                if not user:
                    user = User(username=username, password='', is_active=True, is_staff=True, is_superuser=False)
                return user
            except ldap.INVALID_CREDENTIALS:
                return None
        elif len(ldap_search_results) == 0:
            return None
        else:
            raise TooManyEntries()

    def get_user_by_username(self, username):
        return NotImplementedError

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def bind(self, dn=None, pwd=None):
        con = ldap.initialize(self.ad_url)
        con.simple_bind_s(self.service_account_dn if dn is None else dn,
                          self.service_account_password if pwd is None else pwd)
        return con

    def get_user_info(self, username):
        resultado = 'Error'
        nombre_completo = 'N/A'
        primer_nombre = 'N/A'
        primer_apellido = 'N/A'
        segundo_nombre = 'N/A'
        nombre_usuario = 'N/A'
        email = 'N/A'
        con = ldap.initialize(self.ad_url)
        con.simple_bind_s(self.service_account_dn, self.service_account_password)

        ldap_results = con.search_s(self.search_root, ldap.SCOPE_SUBTREE, '(userPrincipalName=' +
                                    username + ')', ['userPrincipalName', 'mail', 'Sn', 'cn', 'initials',
                                                     'givenName', ])
        if 0 < len(ldap_results) < 2:
            resultado = 'Éxito'
            primer_nombre = ldap_results[0][1]['givenName'][0].decode('utf-8')
            segundo_nombre = ldap_results[0][1]['initials'][0].decode('utf-8') \
                if 'initials' in ldap_results[0][1] else segundo_nombre
            primer_apellido = ldap_results[0][1]['sn'][0].decode('utf-8')
            nombre_completo = ldap_results[0][1]['cn'][0].decode("utf-8")
            nombre_usuario = ldap_results[0][1]['userPrincipalName'][0].decode("utf-8")
            email = ldap_results[0][1]['userPrincipalName'][0].decode("utf-8")
        elif len(ldap_results) == 0:
            resultado = 'No se encontró un usuario con ese nombre.'
        else:
            resultado = 'Se encontraron varios usuarios con ese nombre.'
        return {'resultado': resultado,
                'primer_nombre': primer_nombre,
                'segundo_nombre': segundo_nombre,
                'primer_apellido': primer_apellido,
                'nombre_completo': nombre_completo,
                'nombre_usuario': nombre_usuario,
                'email': email,
                }

    def create_user(self, usuario_nuevo, user_info):
        usuario_nuevo.first_name = user_info['primer_nombre']
        usuario_nuevo.last_name = user_info['primer_apellido']
        usuario_nuevo.email = user_info['email']
        usuario_nuevo.save()
        user_profile = SocialNetworkUser(usuario=usuario_nuevo)
        user_profile.save()
        return usuario_nuevo


class SocialNetworkBackend(ActiveDirectoryBackend):
    def get_user_by_username(self, username):
        username = username.split('@')[0]
        username += '@ramajudicial.pr'
        try:
            user = User.objects.get(email__iexact=username)
        except User.DoesNotExist:
            user = None
        return user

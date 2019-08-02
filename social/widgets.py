import html

from django import forms
from django.conf import settings


class BuscadorDeUsuarioWidget(forms.Widget):
    def __init__(self, url, timeout_milliseconds, attrs=None):
        self.user_lookup_url = url
        self.timeout_milliseconds = timeout_milliseconds
        super(BuscadorDeUsuarioWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None, renderer=None):
        if settings.AUTH_BACKEND.endswith('DummyBackend'):
            search = '''
            function search_and_display_user()
                {
                    elemento_busqueda = document.getElementById("id_buscador_de_usuario");
                    elemento_resultado = document.getElementById("resultado_busqueda");
                    if (elemento_busqueda != null && elemento_busqueda.value.trim().length > 0) {
                        // displayLoadingOverlay(true);
                        var xhr = new XMLHttpRequest();
                        var csrftoken = getCookie('csrftoken');                    

                        xhr.open('POST', '%s', true);
                        xhr.setRequestHeader("X-CSRFToken", csrftoken);
                        xhr.timeout = %s; // time in milliseconds
                        xhr.onload = function() {
                            if (this.readyState == 4 && this.status == 200) { // Request finished with success
                                results = JSON.parse(xhr.responseText);
                                elemento_resultado.innerHTML = 
                                  "<p> <strong> Resultado: </strong>" + results.resultado + "</p> </br>" + 
                                  "<p> <strong> Nombre de Usuario: </strong>" + results.nombre_usuario + "</p> </br>" +
                                  "<p> <strong> Nombre Completo: </strong>" + results.nombre_completo + "</p> </br>" +
                                  "<p> <strong> Correo Electrónico: </strong>" + results.email + "</p> </br>" ;
                            }
                        };

                        var form_data = new FormData();
                        form_data.append('username', elemento_busqueda.value);
                        elemento_resultado.innerHTML = "<p>Buscando...</p>"
                        xhr.send(form_data);  
                    } else {
                        elemento_resultado.innerHTML = "<p>Por favor, indique el nombre de usuario a buscar.</p>"
                        elemento_busqueda.focus()
                    }
                }
            '''
        else:
            search = '''function search_and_display_user()
                {
                    elemento_busqueda = document.getElementById("id_buscador_de_usuario");
                    elemento_resultado = document.getElementById("resultado_busqueda");
                    if (elemento_busqueda != null && elemento_busqueda.value.trim().length > 0) {
                        // displayLoadingOverlay(true);
                        var xhr = new XMLHttpRequest();
                        var csrftoken = getCookie('csrftoken');                    

                        xhr.open('POST', '%s', true);
                        xhr.setRequestHeader("X-CSRFToken", csrftoken);
                        xhr.timeout = %s; // time in milliseconds
                        xhr.onload = function() {
                            if (this.readyState == 4 && this.status == 200) { // Request finished with success
                                elemento_resultado.innerHTML = xhr.responseText;
                                results = JSON.parse(xhr.responseText);
                                elemento_resultado.innerHTML = 
                                  "<p> <strong> Resultado: </strong>" + results.resultado + "</p> </br>" + 
                                  "<p> <strong> Nombre de Usuario: </strong>" + results.nombre_usuario + "</p> </br>" +
                                  "<p> <strong> Nombre Completo: </strong>" + results.nombre_completo + "</p> </br>" +
                                  "<p> <strong> Correo Electrónico: </strong>" + results.email + "</p> </br>" ;

                            } else {
                                elemento_resultado.innerHTML = "<p>Un error del servidor impide la consulta al momento("
                                + this.status + ")</p>";
                            }
                            // displayLoadingOverlay(false);
                        };

                        xhr.ontimeout = function (e) {
                            // XMLHttpRequest timed out. 
                            elemento_resultado.innerHTML = "<p>El servidor no está disponible en estos momentos</p>";
                            // displayLoadingOverlay(false);
                        };
                        var form_data = new FormData();
                        form_data.append('username', elemento_busqueda.value);
                        elemento_resultado.innerHTML = "<p>Buscando...</p>"
                        xhr.send(form_data);  
                    } else {
                        elemento_resultado.innerHTML = "<p>Por favor, indique el nombre de usuario a buscar.</p>"
                        elemento_busqueda.focus()
                    }
                }'''
        html_fragment = \
            """
            <script type="text/javascript" > 
                function getCookie(name) {
                    var cookieValue = null;
                    if (document.cookie && document.cookie !== '') {
                        var cookies = document.cookie.split(';');
                        for (var i = 0; i < cookies.length; i++) {
                            var cookie = cookies[i].trim();
                            // Does this cookie string begin with the name we want?
                            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                                break;
                            }
                        }
                    }
                    return cookieValue;
                }
            """ + search +"""
            </script>
            <tr><td>
                <input id="id_buscador_de_usuario" type="text" name="%s" value=""> &nbsp; &nbsp;
                </td><td><input id="boton_de_busqueda" type="button" name="boton" value="Buscar..." onclick=search_and_display_user("busqueda_btn")> </td></tr>
                <tr><td colspan="2" > <div id="resultado_busqueda">&nbsp;</div> </td></tr>
            
           """
        return html_fragment % (self.user_lookup_url, self.timeout_milliseconds, html.escape(name))


class BuscadorDeUsuarioField(forms.Field):
    def __init__(self, *args, **kwargs):
        kwargs["widget"] = BuscadorDeUsuarioWidget(kwargs.pop('url'), kwargs.pop('timeout_milliseconds'))
        super(BuscadorDeUsuarioField, self).__init__(*args, **kwargs)

    def clean(self, value):
        return value



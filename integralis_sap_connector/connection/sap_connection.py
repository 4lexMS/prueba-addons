import requests
import logging
import json
from odoo import tools

_logger = logging.getLogger(__name__)

class SAP(object):

    def __init__(
        self,
        api_url,
        session_id=None,
        route_id=None
    ):
        """Constructor de la clase SAP
        :param api_url(str): Url de la API
        :param session_id(str): Id se sesión unico proporcionado por SAP al iniciar sesión
        :param route_id(str): Elemento que proporciona el servidor de SAP dentro de cookie
        """
        self.api_url = api_url
        self.session_id = session_id
        self.route_id = route_id
        self.session = requests.Session()
        self.session.verify=False

    def request(self, endpoint, method, params=None, payload=None):
        """Realizar las peticiones a SAP
        :param endpoint: Endpoint ruta o recurso de la API
        :param method: Método HTTP a usar: get, post, put, delete
        :param params (opcional): Llaves y valores que irán en la URL como parametros
        :param payload (opcional): Body del request. El SDK Lo convierte en json
        :returns HTTPResponse: resultado del request.
        """
        params = params or {}
        payload = payload or {}
        response = None
        uri = self.make_path(endpoint)
        headers =  {'Content-Type': 'application/json'}
        cookies = {
            'B1SESSION':self.session_id,
            'ROUTEID':self.route_id
            }
        try:
            if method == "get":
                response = self.session.get(
                    uri,
                    params=params,
                    headers=headers,
                    cookies=cookies,
                    timeout=60
                )
            elif method == "post":
                response = self.session.post(
                    uri,
                    headers=headers,
                    json=payload,
                    cookies=cookies,
                    timeout=60
                    )
        except Exception as ex:
            _logger.error(
                """Error al conectarse con SAP. Detalle del error: %s"""
                % tools.ustr(ex)
            )
            response = requests.Response()
            response._content = json.dumps({"error": tools.ustr(ex)}).encode()
        return response

    def get(self, endpoint, params=None):
        """Realizar solicitudes tipo get a SAP
        :param endpoint: Ruta del recurso de la API
        :param params: Valores que iran en la URL como parametros
        :returns HTTPResponse: Resultado del request
        """
        return self.request(endpoint, "get", params=params)

    def post(self, endpoint, payload=None):
        """Realizar solicitudes tipo POST a SAP
        :param endpoint: Ruta del recurso de la API
        :param payload: Body del request
        :returns HTTPResponse: Resultado del request
        """
        return self.request(endpoint, "post", payload=payload)

    def make_path(self, path):
        """Agregar la ruta completa para llamar a los endpoint
        :param path: Ruta del recurso a solicitar
        : returns pat"""
        if not path.startswith("/"):
            path = "/" + path
        path = self.api_url + "/b1s/v1" + path
        return path

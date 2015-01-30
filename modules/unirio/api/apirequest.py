# -*- coding: utf-8 -*-
from datetime import datetime

import requests

from gluon import current
from apiresult import APIResultObject, APIPOSTResponse, APIPUTResponse, APIDELETEResponse


__all__ = ["UNIRIOAPIRequest"]


class UNIRIOAPIRequest(object):
    """
    UNIRIOAPIRequest is the main class for
    """
    lastQuery = ""
    _versions = {0: "Production", 1: "Development", 2: "Local"}
    baseAPIURL = {0: "https://sistemas.unirio.br/api", 1: "https://teste.sistemas.unirio.br/api",
                  2: "http://localhost:8000/api"}
    timeout = 5  # 5 seconds

    def __init__(self, api_key, server=0, debug=False, cache=current.cache.ram):
        """


        :type cache: gluon.cache.CacheInRam
        :param api_key: The 'API Key' that will the used to perform the requests
        :param server: The server that will used. Production or Development
        """
        self.api_key = api_key
        self.server = server
        self.requests = []
        self.debug = debug
        self.cache = cache

    def _URLQueryParametersWithDictionary(self, params=None):
        """
        The method receiver a dictionary of URL parameters, validates and returns
        as an URL encoded string
        :rtype : dict
        :param params: The parameters for the request. A value of None will
                        send only the API_KEY and FORMAT parameters
        :return: URL enconded string with the valid parameters
        """
        if not params: params = {}

        params.update({"API_KEY": self.api_key, "FORMAT": "JSON"})

        for k, v in params.items():
            if not str(v):
                del params[k]
        return params

    def _URLQueryReturnFieldsWithList(self, fields=[]):
        """
        The method receives a list of fields to be returned as a string of
        concatenated FIELDS parameters
        
        :rtype : dict
        :param fields: A list of strings with valid field names for selected path
        :type fields: list 
        """
        if fields:
            return {'FIELDS': ','.join(fields)}

    def _URLWithPath(self, path):
        """
        The method construct the base URL to be used for requests.

        :rtype : str
        :param path: The API endpoint to use for the request, for example "/ALUNOS"
        :return: Base URL with the provided endpoint
        """
        APIURL = self.baseAPIURL[self.server]
        requestURL = APIURL + "/" + path
        return requestURL

    def __addRequest(self, method, path, params):
        if self.debug:
            self.requests.append({
                "method": method,
                "path": path,
                "params": params,
                "timestamp": datetime.now()
            })

    def URLQueryData(self, params=None, fields=None):
        """
        The method provides the additional data to send to the API server in order to
        perform a request.

        :rtype : str
        :param params: dictionary with URL parameters
        :param fields: list with de desired return fields. Empty list or None will return all Fields
        :return:
        """
        parameters = self._URLQueryParametersWithDictionary(params)
        returnFields = self._URLQueryReturnFieldsWithList(fields)
        # data = parameters + returnFields if returnFields else parameters
        if returnFields:
            parameters.update(returnFields)
        return parameters

    def payload(self, params=None):
        """
        O payload de um POST/PUT obrigatoriamente devem ser do tipo dict.

        :type params: dict
        :param params: Dicionário com os dados a serem inseridos
        :rtype : dict
        :return: Dicionário processado a ser enviado para a Request
        """
        payload = dict(params)
        payload.update({
            "API_KEY": self.api_key
        })
        return payload

    def __cacheHash(self, path, params):
        """
        Método utilizado para gerar um hash único para ser utilizado como chave de um cache

        :param path: String correspondente a um endpoint
        :param params: Dicionário de parâmetros
        :return: String a ser utilizada como chave de um cache
        """
        return path + str(hash(frozenset(params.items())))

    def performGETRequest(self, path, params=None, fields=None, cached=0):
        """
        Método para realizar uma requisição GET. O método utiliza a API Key fornecida ao instanciar 'UNIRIOAPIRequest'
        e uma chave inválida resulta em um erro HTTP

        :type path: str
        :param path: string with an API ENDPOINT
        :type params: dict
        :param params: dictionary with URL parameters
        :type fields: list
        :param fields: list with de desired return fields. Empty list or None will return all Fields
        :type cached: int
        :param cached int for cached expiration time. 0 means no cached is applied
        :rtype : APIResultObject
        :raises Exception may raise an exception if not able to instantiate APIResultObject
        """

        def _get():
            url = self._URLWithPath(path)
            payload = self.URLQueryData(params, fields)
            print url
            try:
                r = requests.get(url, params=payload)
                resultObject = APIResultObject(r, self)
                self.lastQuery = url
                return resultObject
            except ValueError as e:
                if cached:
                    return None
                else:
                    raise e

        if cached:
            uniqueHash = self.__cacheHash(path, params)
            projeto = self.cache(
                uniqueHash,
                lambda: _get(),
                time_expire=cached
            )
            print uniqueHash
            return projeto
        else:
            return _get()


    def performPOSTRequest(self, path, params):
        """

        :rtype : APIPOSTResponse
        """
        url = self._URLWithPath(path)
        payload = self.payload(params)

        response = requests.post(url, payload, verify=False)
        self.__addRequest("POST", path, payload)
        return APIPOSTResponse(response, self)

    def performDELETERequest(self, path, params):
        """
        :type path: str
        :param path: string with an API ENDPOINT

        :param id:
        :rtype : unirio.api.apiresult.APIDELETEResponse
        """
        url = self._URLWithPath(path)
        payload = self.URLQueryData(params)
        contentURI = "%s?%s" % (url, payload)

        req = requests.delete(contentURI, verify=False)
        r = APIDELETEResponse(req, self)

        return r

    def performPUTRequest(self, path, params):
        url = self._URLWithPath(path)
        payload = self.payload(params)
        response = requests.put(url, payload, verify=False)

        return APIPUTResponse(response, self)

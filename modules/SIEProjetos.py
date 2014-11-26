# coding=utf-8
from gluon import current
from unirio.api import UNIRIOAPIRequest

class SIEProjetos(object):
    def __init__(self):
        self.path = "PROJETOS"
        self.api = UNIRIOAPIRequest(current.kAPIKey)

    def getProjetos(self):
        params = {
            'LMIN': 0,
            'LMAX': 99999
        }
        fields = [
            'ID_PROJETO',
            'TITULO'
        ]
        meuResultado = self.api.performGETRequest(self.path, params)
        return meuResultado

    def salvarProjeto(self, projeto):
        """


        :type projeto: dict
        :param projeto: Um dicionário contendo os valores do novo projeto
        :return: APIPOSTResponse
        """
        return self.api.performPOSTRequest(self.path, projeto)
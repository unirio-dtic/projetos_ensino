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
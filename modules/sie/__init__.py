from unirio.api import UNIRIOAPIRequest
from gluon import current

__all__ = ["SIEDocumento", "SIEFuncionarios", "SIEProjetos", "SIEFluxos", "SIETabEstruturada"]


class SIE(object):
    def __init__(self):
        self.api = UNIRIOAPIRequest(current.kAPIKey, 1)
        self.cacheTime = 86400  # Um dia
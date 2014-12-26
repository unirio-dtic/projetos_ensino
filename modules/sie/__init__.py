from unirio.api import UNIRIOAPIRequest
from gluon import current

__all__ = ["SIEDocumento", "SIEFuncionarios", "SIEProjetos", "SIEFluxos"]


class SIE(object):
    def __init__(self):
        self.api = UNIRIOAPIRequest(current.kAPIKey)
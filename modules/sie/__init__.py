from gluon import current

__all__ = ["SIEDocumento", "SIEFuncionarios", "SIEProjetos", "SIEFluxos", "SIETabEstruturada"]


class SIE(object):
    def __init__(self):
        self.api = current.api
        self.cacheTime = 86400  # Um dia
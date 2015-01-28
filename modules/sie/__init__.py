from gluon import current

__all__ = ["SIEDocumento", "SIEFuncionarios", "SIEProjetos", "SIEFluxos", "SIETabEstruturada", "SIEServidores"]


class SIE(object):
    def __init__(self, api=current.api):
        """

        :type api: unirio.api.apirequest.UNIRIOAPIRequest
        :param api: UNIRIO API
        """
        self.api = api
        self.cacheTime = 86400  # Um dia
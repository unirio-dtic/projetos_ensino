from sie import SIE

__all__ = ["SIEServidores"]


class SIEServidores(SIE):
    def __init__(self):
        super(SIEServidores, self).__init__()
        self.path = "V_SERVIDORES"

    def getServidorByCPF(self, CPF):
        params = {
            "CPF_SEM_MASCARA": CPF,
            "LMIN": 0,
            "LMAX": 1
        }
        return self.api.performGETRequest(self.path, params, cached=self.cacheTime).content[0]
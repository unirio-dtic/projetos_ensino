from gluon import current
from unirio.api import UNIRIOAPIRequest


class Xpto(object):
    def __init__(self):
        self.api = UNIRIOAPIRequest(current.kAPIKey)


class SIEProjetos(Xpto):
    def __init__(self):
        super(SIEProjetos, self).__init__()
        self.path = "PROJETOS"


    def getProjetos(self):
        params = {
            'LMIN': 0,
            'LMAX': 20
        }
        fields = [
            'ID_PROJETO',
            'TITULO',
            'TIPO_PUBLICO_TAB',
            'TIPO_PUBLICO_ITEM',
            'DT_ALTERACAO'
        ]
        meuResultado = self.api.performGETRequest(self.path, params, fields)
        return meuResultado

    def salvarProjeto(self, projeto):
        return self.api.performPOSTRequest(self.path, projeto)


class SIEClassificacoesPrj(Xpto):
    def __init__(self):
        super(SIEClassificacoesPrj, self).__init__()
        self.path = "CLASSIFICACOES_PRJ"

    def getClassificacoesPrj(self):
        """

        :rtype : list
        :return: Essa merda retorna blab lab la
        """
        params = {
            'CLASSIFICACAO_ITEM': 1,
            'CODIGO': 1
        }
        fields = [
            'ID_CLASSIFICACAO',
            'DESCRICAO'
        ]
        return self.api.performGETRequest(self.path, params, fields).content
# coding=utf-8
from sie import SIE

__all__ = [
    "SIETabEstruturada"
]


class SIETabEstruturada(SIE):
    def __init__(self):
        super(SIETabEstruturada, self).__init__()
        self.path = "TAB_ESTRUTURADA"

    def descricaoDeItem(self, ITEM_TABELA, COD_TABELA):
        """
        Método de conveniência para

        :type ITEM_TABELA: int
        :type COD_TABELA: int
        :param ITEM_TABELA:
        :param COD_TABELA:
        :return:
        """
        params = {
            "ITEM_TABELA": ITEM_TABELA,
            "COD_TABELA": COD_TABELA,
            "LMIN": 0,
            "LMAX": 1
        }
        fields = ["DESCRICAO"]
        try:
            return self.api.performGETRequest(self.path, params, fields, cached=self.cacheTime).first()["DESCRICAO"]
        except AttributeError:
            raise AttributeError("Descrição não encontrada")
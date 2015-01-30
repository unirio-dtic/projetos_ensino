# coding=utf-8
from sie import SIE

__all__ = [
    "SIETabEstruturada"
]


class SIETabEstruturada(SIE):
    def __init__(self):
        super(SIETabEstruturada, self).__init__()
        self.path = "TAB_ESTRUTURADA"
        self.cacheTime *= 2

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
            raise AttributeError("Descrição não encontrada.")

    def itemsDeCodigo(self, COD_TABELA):
        """
        Dado um COD_TABELA, a função retornará uma lista de dicionários de valores possíveis de ITEM_TABELA e sua
        DESCRICAO

        :param COD_TABELA: Identificador de único de um domínio de valores de uma tabela
        :raise AttributeError: Uma exception é disparada caso nenhum item seja encontrado para o COD_TABELA
        :rtype : list
        :return: Uma lista de dicionários contendo as chaves `ITEM_TABELA` e `COD_TABELA`
        """
        params = {
            "COD_TABELA": COD_TABELA,
            "LMIN": 0,
            "LMAX": 99999
        }
        fields = ["ITEM_TABELA", "DESCRICAO"]
        try:
            items = self.api.performGETRequest(self.path, params, fields, cached=self.cacheTime).content
            # Primeiro item de uma de ITEMS de uma TABELA é sempre a descrição do conteúdo
            return items[1:]
        except AttributeError:
            raise AttributeError("Nenhum item encontreado para este código.")
# coding=utf-8
from sie import SIE

__all__ = ['SIEBolsas', 'SIEBolsistas']


class SIEBolsas(SIE):
    def __init__(self):
        super(SIEBolsas, self).__init__()
        self.path = "BOLSAS"

    def getBolsa(self, ID_BOLSA):
        """
        Dado um identificador único da tabela de BOLSAS, o método retorna um dicionário equivalente a esta entrada.
        A requisição é cacheada.

        :type ID_BOLSA: int
        :param ID_BOLSA: Identificador único de uma bolsa na tabela BOLSAS
        :return: Um dicionário correspondente a uma entrada na tabela BOLSAS
        :rtype: dict
        """
        params = {
            "ID_BOLSA": ID_BOLSA,
            "LMIN": 0,
            "LMAX": 1
        }
        return self.api.performGETRequest(self.path, params, cached=self.cacheTime).content[0]


class SIEBolsistas(SIE):
    def __init__(self):
        super(SIEBolsistas, self).__init__()
        self.path = "BOLSISTAS"

    def criarBolsista(self, bolsa, edicao, aluno):
        """

        :type aluno: dict
        :param aluno: Um dicionário contendo as entradas ID_PESSOA e ID_CURSO_ALUNO
        :type bolsa: dict
        :param bolsa: Uma entrada na tabela BOLSAS
        :type edicao: Storage
        :param edicao: Uma entrada da tabela db.edicoes
        :rtype : unirio.api.apiresult.APIPostResponse
        """
        params = {
            "DT_INICIO": edicao.dt_inicial_projeto,
            "ID_BOLSA": bolsa['ID_BOLSA'],
            "ID_CURSO_ALUNO": aluno['ID_CURSO_ALUNO'],
            "ID_PESSOA": aluno['ID_PESSOA'],
            "NUM_HORAS": 20,
            "SITUACAO_BOLSISTA": "A",
            "VL_BOLSA": bolsa['VL_BOLSA']
        }
        return self.api.performPOSTRequest(self.path, params)


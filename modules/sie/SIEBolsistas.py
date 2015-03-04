# coding=utf-8
from datetime import date
from sie import SIE

__all__ = ['SIEBolsas', 'SIEBolsistas']


class SIEBolsas(SIE):
    def __init__(self):
        super(SIEBolsas, self).__init__()
        self.path = 'BOLSAS'

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
            'ID_BOLSA': ID_BOLSA,
            'LMIN': 0,
            'LMAX': 1
        }
        fields = [
            'ID_BOLSA',
            'COD_BOLSA',
            'DESCR_BOLSA',
            'VL_BOLSA',
            'VAGAS_OFERECIDAS',
            'TIPO_BOLSA',
            'SITUACAO_BOLSA',
            'IND_PERCENTUAL'
        ]
        return self.api.performGETRequest(self.path, params, fields, cached=self.cacheTime).content[0]


class SIEBolsistas(SIE):
    def __init__(self):
        super(SIEBolsistas, self).__init__()
        self.path = "BOLSISTAS"

    def criarBolsista(self, bolsa, edicao, aluno, projeto):
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
            'DT_INICIO': edicao.dt_inicial_projeto,
            'DT_INCLUSAO': date.today(),
            'ID_BOLSA': bolsa['ID_BOLSA'],
            'ID_CURSO_ALUNO': aluno['ID_CURSO_ALUNO'],
            'ID_UNIDADE': projeto['ID_UNIDADE'],
            'ID_PESSOA': aluno['ID_PESSOA'],
            'NUM_HORAS': 20,
            'SITUACAO_BOLSISTA': 'A',
            'VL_BOLSA': bolsa['VL_BOLSA'],
        }
        return self.api.performPOSTRequest(self.path, params)

    def getBolsista(self, ID_BOLSISTA, cached=True):
        params = {
            'ID_BOLSISTA': ID_BOLSISTA,
            'LMIN': 0,
            'LMAX': 1
        }
        return self.api.performGETRequest(self.path, params, cached=self.cacheTime if cached else 0)

    def atualizarDadosBancarios(self, ID_BOLSISTA, dados):
        """
        Método utilizado para atualizar dados bancários de um bolsista.

        :type ID_BOLSISTA: int
        :param ID_BOLSISTA: Identificador único de um bolsista na tabela BOLSISTAS
        :type dados: dict
        :param dados: dicionário de dados contendo as chaves ID_AGENCIA e CONTA_CORRENTE
        """
        params = {
            'ID_BOLSISTA': ID_BOLSISTA,
            'ID_AGENCIA': dados['ID_AGENCIA'],
            'CONTA_CORRENTE': dados['CONTA_CORRENTE']
        }
        return self.api.performPUTRequest(self.path, params)

    def inativarBolsista(self, ID_BOLSISTA):
        """
        Método utilizado para remover um bolsista. Dado um bolsista, o método INATIVA sua entrada e registra a data.

        :type ID_BOLSISTA: int
        :param ID_BOLSISTA: Identificador único de um bolsista na tabela BOLSISTAS
        """
        params = {
            'ID_BOLSISTA': ID_BOLSISTA,
            'SITUACAO_BOLSISTA': 'I',
            'DT_TERMINO': date.today()
        }
        return self.api.performPUTRequest(self.path, params)

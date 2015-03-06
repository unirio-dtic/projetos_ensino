# coding=utf-8
from csv import DictWriter
from twisted.names import cache
from avaliacao import Avaliacao
from gluon import current, URL, A


__author__ = 'diogomartins'


class DictUnicodeProxy(object):
    def __init__(self, d):
        self.d = d

    def __iter__(self):
        return self.d.__iter__()

    def get(self, item, default=None):
        i = self.d.get(item, default)
        if isinstance(i, unicode):
            return i.encode('latin1')
        return i

def salvarCSV(content, filename):
    """
    :type content: list
    :param content: Lista de dicionários que se tornarão linhas do csv
    :type filename: str
    :param filename: Nome do arquivo que será salva como `filename.csv`
    :rtype : gluon.A
    :return: Um link para download do arquivo salvo
    """
    with open(current.request.folder + 'static/%s.csv' % filename, 'w') as outfile:
        writer = DictWriter(outfile, content[0].keys())
        writer.writeheader()
        for p in content:
            writer.writerow(DictUnicodeProxy(p))
        return A("Baixar relatório", _href=URL('static', '%s.csv?attachment' % filename))


class Deferimento(object):
    def __init__(self, edicao):
        self.db = current.db
        self.api = current.api
        self.edicao = edicao
        self.cacheTime = 800
        self.fields = ("ID_PROJETO", "COORDENADOR", "NOME_DISCIPLINA", "NOME_UNIDADE", "TITULO")
        self.avaliacao = Avaliacao()

        bolsas = self.db((self.db.bolsas.id_projeto == self.db.projetos.id_projeto) & (
            self.db.projetos.edicao == self.edicao.id)).select(self.db.bolsas.ALL,
                                                               cache=(current.cache.ram, self.cacheTime))
        self.bolsas = {b.id_projeto: b.quantidade_bolsas for b in bolsas}
        self.bolsasCount = 0

    def __getProjetos(self, SITUACAO_ITEM):
        try:
            projetos = self.api.performGETRequest("V_PROJETOS_DADOS", {
                "ID_CLASSIFICACAO": 40161,  # Projeto de ensino
                "ORDERBY": "COORDENADOR",
                "SORT": "ASC",
                "SITUACAO_ITEM": SITUACAO_ITEM,
                "DT_INICIAL": self.edicao.dt_inicial_projeto,
                "LMIN": 0,
                "LMAX": 5000
            }, self.fields, cached=self.cacheTime).content

            for p in projetos:
                p.update({
                    "AVALIADOR": self.avaliacao.getAvaliador(p['ID_PROJETO']),
                    "BOLSAS": self.bolsas[p['ID_PROJETO']]
                })
                self.bolsasCount += self.bolsas[p['ID_PROJETO']]

            return projetos
        except ValueError:
            return []

    def projetosDeferidos(self):
        return self.__getProjetos(2)

    def projetosIndeferidos(self):
        return self.__getProjetos(9)

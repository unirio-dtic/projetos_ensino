# coding=utf-8
from sie.SIETabEstruturada import SIETabEstruturada
from sie.SIEProjetos import SIEParticipantesProjs
from gluon.html import *

__all__ = [
    "TableAcompanhamento",
    "TableAvaliacao"
]


class TableAcompanhamento(object):
    def __init__(self, participacoes, projetos):
        self.headers = ("Data de registro", "Título", "Função", "Avaliação")
        self.participacoes = participacoes
        self.projetos = projetos

    def funcao(self, projeto):
        for i, dic in enumerate(self.participacoes):
            if dic["ID_PROJETO"] == projeto["ID_PROJETO"]:
                return SIEParticipantesProjs().descricaoDeFuncaoDeParticipante(self.participacoes[i])

    def avaliacao(self, projeto):
        try:
            return SIETabEstruturada().descricaoDeItem(projeto["SITUACAO_ITEM"], projeto["SITUACAO_TAB"])
        except AttributeError:
            return "Situação não cadastrada"

    def printTable(self):
        return TABLE(
            THEAD(TR([TH(h) for h in self.headers])),
            [TR(p['DT_REGISTRO'], p['TITULO'], self.funcao(p), self.avaliacao(p)) for p in self.projetos if p]
        )


class TableAvaliacao(object):
    def __init__(self, projetos):
        self.headers = ("Data de registro", "Título", "Arquivos", "Situação", "Avaliar")
        self.projetos = projetos

    def situacao(self, projeto):
        try:
            return SIETabEstruturada().descricaoDeItem(projeto["SITUACAO_ITEM"], projeto["SITUACAO_TAB"])
        except AttributeError:
            return "Situação não cadastrada"

    def avaliacao(self, projeto):
        try:
            return SIETabEstruturada().descricaoDeItem(projeto["AVALIACAO_ITEM"], projeto["AVALIACAO_TAB"])
        except AttributeError:
            return "Avaliação não cadastrada"

    def arquivos(self):
        try:
            pass
        except:
            pass

    def printTable(self):
        return TABLE(
            THEAD(TR([TH(h) for h in self.headers])),
            [TR(p['DT_REGISTRO'], p['TITULO'], self.arquivos(p), self.situacao(p), self.avaliacao(p)) for p in self.projetos if p]
        )
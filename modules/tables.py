# coding=utf-8
from gluon import current
from sie.SIETabEstruturada import SIETabEstruturada
from sie.SIEProjetos import SIEParticipantesProjs
from gluon.html import *

__all__ = [
    "TableAcompanhamento",
    "TableAvaliacao"
]


class TableAcompanhamento(object):
    def __init__(self, participacoes, projetos):
        self.headers = ("Data de registro", "Num. Processo", "Título", "Função", "Avaliação", "Arquivos")
        self.participacoes = participacoes
        self.projetos = projetos

    def funcao(self, projeto):
        for i, dic in enumerate(self.participacoes):
            if dic["ID_PROJETO"] == projeto["ID_PROJETO"]:
                return SIEParticipantesProjs().descricaoDeFuncaoDeParticipante(self.participacoes[i])

    def avaliacao(self, projeto):
        try:
            return SIETabEstruturada().descricaoDeItem(projeto["AVALIACAO_ITEM"], projeto["AVALIACAO_TAB"])
        except AttributeError:
            return "Avaliação não cadastrada"

    def arquivos(self, projeto):
        arquivos = current.db(current.db.projetos.id_projeto == projeto["ID_PROJETO"]).select()
        return [A(arquivo["anexo_nome"]) for arquivo in arquivos]

    def printTable(self):
        return TABLE(
            THEAD(TR([TH(h) for h in self.headers])),
            TBODY([TR(p['DT_REGISTRO'], p['NUM_PROCESSO'], p['TITULO'], self.funcao(p), self.avaliacao(p), self.arquivos(p)) for p in
                   self.projetos if p])
        )


class TableAvaliacao(object):
    def __init__(self, projetos):
        self.headers = ("Data de registro", "Num. Processo", "Título", "Arquivos", "Situação", "Avaliação", "Avaliar")
        self.projetos = projetos

    def situacao(self, projeto):
        try:
            return SIETabEstruturada().descricaoDeItem(projeto["SITUACAO_ITEM"], projeto["SITUACAO_TAB"])
        except AttributeError:
            return "Aguardando..."

    def avaliacao(self, projeto):
        try:
            return SIETabEstruturada().descricaoDeItem(projeto["AVALIACAO_ITEM"], projeto["AVALIACAO_TAB"])
        except AttributeError:
            return "Avaliação não cadastrada"

    def arquivos(self, projeto):
        try:
            pass
        except:
            pass

    def avaliar(self, projeto):
        aprovar = {"ID_PROJETO": projeto["ID_PROJETO"], "action": "aprovar"}
        reprovar = {"ID_PROJETO": projeto["ID_PROJETO"], "action": "reprovar"}

        return (
            A("Aprovar", _id=projeto["ID_PROJETO"], callback=URL('adm', 'avaliacaoAjax', vars=aprovar),
              target="callback-placeholder"),
            " | ",
            A("Reprovar", _id=projeto["ID_PROJETO"], callback=URL('adm', 'avaliacaoAjax', vars=reprovar),
              target="callback-placeholder"),
        )

    def printTable(self):
        return TABLE(
            THEAD(TR([TH(h) for h in self.headers])),
            TBODY([TR(p['DT_REGISTRO'], p['NUM_PROCESSO'], p['TITULO'], self.arquivos(p), self.situacao(p),
                      self.avaliacao(p), self.avaliar(p)) for p in self.projetos if p])
        )
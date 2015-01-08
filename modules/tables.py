# coding=utf-8
from gluon import current
from sie.SIETabEstruturada import SIETabEstruturada
from sie.SIEProjetos import SIEParticipantesProjs
from gluon.html import *

__all__ = [
    "TableAcompanhamento",
    "TableAvaliacao"
]


class TableProjetos(object):
    def __init__(self, projetos):
        self.projetos = projetos

    def arquivos(self, projeto):
        arquivos = current.db(current.db.projetos.id_projeto == projeto["ID_PROJETO"]).select()
        return [A(arquivo["anexo_nome"], _href=URL(f='download', args=arquivo["arquivo"])) for arquivo in arquivos]

    def avaliacao(self, projeto):
        try:
            return SIETabEstruturada().descricaoDeItem(projeto["AVALIACAO_ITEM"], projeto["AVALIACAO_TAB"])
        except AttributeError:
            return "Avaliação não cadastrada"


class TableAcompanhamento(TableProjetos):
    def __init__(self, participacoes, projetos):
        super(TableAcompanhamento, self).__init__(projetos)
        self.headers = ("Data de registro", "Num. Processo", "Título", "Função", "Avaliação", "Arquivos")
        self.participacoes = participacoes

    def funcao(self, projeto):
        for i, dic in enumerate(self.participacoes):
            if dic["ID_PROJETO"] == projeto["ID_PROJETO"]:
                return SIEParticipantesProjs().descricaoDeFuncaoDeParticipante(self.participacoes[i])

    def disciplina(self, projeto):
        pass
        # return SIEClassificacoesPrj().

    def printTable(self):
        return TABLE(
            THEAD(TR([TH(h) for h in self.headers])),
            TBODY([TR(p['DT_REGISTRO'], p['NUM_PROCESSO'], p['TITULO'], self.funcao(p), self.avaliacao(p), self.arquivos(p)) for p in
                   self.projetos if p])
        )


class TableAvaliacao(TableProjetos):
    def __init__(self, projetos):
        super(TableAvaliacao, self).__init__(projetos)
        self.headers = ("Data de registro", "Num. Processo", "Título", "Arquivos", "Situação", "Avaliação", "Avaliar")

    def situacao(self, projeto):
        try:
            return SIETabEstruturada().descricaoDeItem(projeto["SITUACAO_ITEM"], projeto["SITUACAO_TAB"])
        except AttributeError:
            return "Aguardando..."

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
# coding=utf-8
from gluon import current
from sie.SIETabEstruturada import SIETabEstruturada
from sie.SIEProjetos import SIEParticipantesProjs, SIEProjetos
from gluon.html import *

__all__ = [
    "TableAcompanhamento",
    "TableAvaliacao"
]


class TableProjetos(object):
    def __init__(self, projetos):
        """

        :type projetos: list
        """
        self.projetos = projetos

        projetosIds = [p["ID_PROJETO"] for p in self.projetos]
        bolsas = current.db(current.db.bolsas.id_projeto.belongs(projetosIds)).select()
        self.bolsas = {bolsa.id_projeto: bolsa.quantidade_bolsas for bolsa in bolsas}

    def arquivos(self, projeto):
        arquivos = current.db(current.db.projetos.id_projeto == projeto["ID_PROJETO"]).select()
        if len(arquivos) > 3:
            n = 1
        return UL([A(arquivo["anexo_nome"], _href=URL(f='download', args=arquivo["arquivo"])) for arquivo in arquivos])

    def avaliacao(self, projeto):
        try:
            return SIETabEstruturada().descricaoDeItem(projeto["AVALIACAO_ITEM"], projeto["AVALIACAO_TAB"])
        except AttributeError:
            return "Avaliação não cadastrada"

    def bolsa(self, projeto):
        try:
            return str(self.bolsas[projeto["ID_PROJETO"]])
        except KeyError:
            return "Indefinido"


class TableAcompanhamento(TableProjetos):
    def __init__(self, participacoes, projetos):
        super(TableAcompanhamento, self).__init__(projetos)
        self.headers = ("Data de registro", "Num. Processo", "Título", "Função", "Avaliação", "Qtd. Bolsas", "Arquivos")
        self.participacoes = participacoes

    def funcao(self, projeto):
        for i, dic in enumerate(self.participacoes):
            if dic["ID_PROJETO"] == projeto["ID_PROJETO"]:
                try:
                    return SIEParticipantesProjs().descricaoDeFuncaoDeParticipante(self.participacoes[i])
                except TypeError:
                    return 'Indefinido'

    def disciplina(self, projeto):
        pass
        # return SIEClassificacoesPrj().

    def printTable(self):
        return TABLE(
            THEAD(TR([TH(h) for h in self.headers])),
            TBODY([TR(p['DT_REGISTRO'], p['NUM_PROCESSO'], p['TITULO'], self.funcao(p), self.avaliacao(p), self.bolsa(p), self.arquivos(p)) for p in
                   self.projetos if p])
        )


class TableAvaliacao(TableProjetos):
    def __init__(self, projetos):
        super(TableAvaliacao, self).__init__(projetos)
        self.headers = ("Num. Processo", "Data de registro", "Título", "Arquivos", "Situação", "Avaliação", "Qtd. Bolsas", "Avaliar")

    def situacao(self, projeto):
        try:
            return SIETabEstruturada().descricaoDeItem(projeto["SITUACAO_ITEM"], projeto["SITUACAO_TAB"])
        except AttributeError:
            return "Aguardando..."

    def avaliar(self, projeto):
        aprovar = {"ID_PROJETO": projeto["ID_PROJETO"], "action": "aprovar"}
        reprovar = {"ID_PROJETO": projeto["ID_PROJETO"], "action": "reprovar"}

        if not SIEProjetos.isAvaliado(projeto):
            uniqueDOMid = "avaliar%d" % projeto["ID_PROJETO"]

            return SPAN(
                A("Aprovar", _id=projeto["ID_PROJETO"], callback=URL('adm', 'avaliacaoAjax', vars=aprovar),
                  target=uniqueDOMid),
                " | ",
                A("Reprovar", _id=projeto["ID_PROJETO"], callback=URL('adm', 'avaliacaoAjax', vars=reprovar),
                  target=uniqueDOMid),
                _id=uniqueDOMid
            )
        else:
            return "Avaliado"

    def printTable(self):
        return TABLE(
            THEAD(TR([TH(h) for h in self.headers])),
            TBODY([TR(p['NUM_PROCESSO'], p['DT_REGISTRO'], p['TITULO'], self.arquivos(p), self.situacao(p),
                      self.avaliacao(p), self.bolsa(p), self.avaliar(p)) for p in self.projetos if p])
        )
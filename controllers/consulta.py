# coding=utf-8
from tables import TableAcompanhamento
from sie.SIEProjetos import SIEParticipantesProjs, SIEProjetos


def index():
    if not session.funcionario:
        redirect(URL("registro", "index"))
    session.funcionario["ID_PESSOA"] = 49

    participacoes = SIEParticipantesProjs().getParticipacoes(session.funcionario)
    projetos = [SIEProjetos().getProjeto(projeto["ID_PROJETO"]) for projeto in participacoes.content]

    tabela = TableAcompanhamento(participacoes.content, projetos)

    return dict(
        tabela=tabela.printTable(),
        projetos=projetos
    )
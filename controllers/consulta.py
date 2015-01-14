# coding=utf-8
from tables import TableAcompanhamento
from sie.SIEProjetos import SIEParticipantesProjs, SIEProjetos


def index():
    if not session.funcionario:
        redirect(URL("registro", "index"))

    # TODO lógica correta mas no ainda está feio...
    participacoes = SIEParticipantesProjs().getParticipacoes(session.funcionario)
    projetosLocais = db(db.projetos.id_funcionario == session.funcionario['ID_FUNCIONARIO']).select(db.projetos.id_projeto)
    ids = [p.id_projeto for p in projetosLocais]

    projetos = [SIEProjetos().getProjeto(projeto["ID_PROJETO"]) for projeto in participacoes.content if projeto['ID_PROJETO'] in ids]

    tabela = TableAcompanhamento(participacoes.content, projetos)

    return dict(
        tabela=tabela.printTable(),
        projetos=projetos
    )


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)
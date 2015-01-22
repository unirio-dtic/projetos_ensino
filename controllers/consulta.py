# coding=utf-8
from tables import TableAcompanhamento
from sie.SIEProjetos import SIEParticipantesProjs, SIEProjetos


def index():
    if not session.funcionario:
        redirect(URL("default", "index"))

    # TODO lógica correta mas no ainda está feio...
    participacoes = SIEParticipantesProjs().getParticipacoes(session.funcionario)
    projetosLocais = db(db.projetos.id_funcionario == session.funcionario['ID_FUNCIONARIO']).select(db.projetos.id_projeto)
    ids = [p.id_projeto for p in projetosLocais]

    projetos = [SIEProjetos().getProjeto(projeto["ID_PROJETO"]) for projeto in participacoes.content if projeto['ID_PROJETO'] in ids]

    tabela = TableAcompanhamento(participacoes.content, projetos)
    try:
        email = api.performGETRequest("V_SERVIDORES_EMAIL", {"ID_PESSOA": session.funcionario['ID_PESSOA']}).content[0]['DESCR_MAIL']
        alert = "Você receberá alertas de avaliação de projeto no email: %s" % str(email)
        alert_class = "alert-info"
    except ValueError:
        alert = "Seu email não pode ser recuperado. Entre em contato com o setor de cadastro da PROGREPE para normalizar sua situação."
        alert_class = "alert-danger"

    return dict(
        tabela=tabela.printTable(),
        projetos=projetos,
        alert=alert,
        alert_class=alert_class
    )


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)
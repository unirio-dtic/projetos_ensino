# coding=utf-8
from unirio.api.apiresult import APIException
from sie.SIEProjetos import SIEProjetos
from gluon.tools import Crud
from tables import TableAvaliacao


@auth.requires(auth.has_membership('PROAD') or auth.has_membership('DTIC'))
def cadastro_edicoes():
    edicoes = Crud(db).select(db.edicao)
    form = SQLFORM(db.edicao)

    if form.process().accepted:
        response.flash = 'form accepted'

    return dict(
        edicoes=edicoes if edicoes else "Nenhuma edição cadastrada",
        form=form
    )


# @edicao.requires_edicao()
@auth.requires(auth.has_membership('PROAD') or auth.has_membership('DTIC'))
def avaliacao():
    if not current.session.edicao:
        redirect(URL("default", "edicoes"))

    ID_CLASSIFICACAO_ENSINO = 40161
    projetos = SIEProjetos().projetosDeEnsino(session.edicao, {"ID_CLASSIFICACAO": ID_CLASSIFICACAO_ENSINO})

    table = TableAvaliacao(projetos)

    return dict(
        projetos=projetos,
        table=table.printTable()
    )


@auth.requires(auth.has_membership('PROAD') or auth.has_membership('DTIC'))
def avaliacaoAjax():
    try:
        if request.vars.action == "aprovar":
            SIEProjetos().avaliarProjeto(request.vars.ID_PROJETO, 2)
        else:
            SIEProjetos().avaliarProjeto(request.vars.ID_PROJETO, 9)
        return dict(m="Avaliado com sucesso")
    except APIException as e:
        return dict(m=e.message)


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)
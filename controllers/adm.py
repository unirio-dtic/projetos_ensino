# coding=utf-8
from datetime import datetime

from avaliacao import Avaliacao
from mail import MailAvaliacao
from forms import FormPerguntas
from unirio.api.apiresult import APIException
from sie.SIEProjetos import SIEProjetos
from tables import TableAvaliacao, TableDeferimento


@auth.requires(auth.has_membership('PROGRAD') or auth.has_membership('DTIC'))
def cadastro_edicoes():
    db.edicao.id.readable = False
    grid = SQLFORM.grid(
        query=db.edicao,
        orderby=db.edicao.nome,
        deletable=False,
        csv=False
    )
    return dict(grid=grid)


def cadastro_perguntas():
    db.avaliacao_perguntas.id.readable = False
    grid = SQLFORM.grid(
        query=db.avaliacao_perguntas.edicao==db.edicao.id,
        fields=(db.edicao.nome, db.avaliacao_perguntas.pergunta),
        field_id=db.avaliacao_perguntas.id,
        orderby=db.edicao.nome,
        deletable=False,
        csv=False
    )
    return dict(grid=grid)


# @edicao.requires_edicao()
@auth.requires(auth.has_membership('PROGRAD') or auth.has_membership('DTIC'))
def avaliacao():
    if not current.session.edicao:
        redirect(URL("default", "edicoes"))

    ID_CLASSIFICACAO_ENSINO = 40161
    projetos = SIEProjetos().projetosDeEnsino(session.edicao, {"ID_CLASSIFICACAO": ID_CLASSIFICACAO_ENSINO})

    ids = [p['ID_PROJETO'] for p in projetos]
    table = TableAvaliacao(projetos)

    return dict(
        projetos=projetos,
        table=table.printTable()
    )


@auth.requires(auth.has_membership('admin') or auth.has_membership('DTIC'))
def avaliadores():
    grid = SQLFORM.grid(
        query=db.auth_membership,
        editable=False,
        deletable=auth.has_membership('DTIC'),
        details=False,
        csv=False
    )
    return dict(grid=grid)


@auth.requires(auth.has_membership('PROGRAD') or auth.has_membership('DTIC'))
def aprovarAjax():
    try:
        SIEProjetos().avaliarProjeto(request.vars.ID_PROJETO, 2)
        Avaliacao().salvarAvaliacao(request.vars.ID_PROJETO)
        try:
            coordenador = current.api.performGETRequest(
                "V_SERVIDORES_EMAIL",
                {
                    "ID_PESSOA": SIEProjetos().getCoordenador(request.vars.ID_PROJETO)["ID_PESSOA"]
                }
            ).content[0]
            email = MailAvaliacao(coordenador)
            email.sendConfirmationEmail()
        except Exception:
            session.flash = "Não foi possível enviar email de confirmação."
        return dict(m="Avaliado com sucesso")
    except APIException as e:
        return dict(m=e.message)


@auth.requires(auth.has_membership('PROGRAD') or auth.has_membership('DTIC'))
def avaliacaoPerguntas():
    # TODO deveria ser um decorator
    if Avaliacao().isAvaliado(request.vars.ID_PROJETO):
        session.flash = "Este projeto já foi avaliado."
        redirect(URL('adm', 'avaliacao'))

    projeto = SIEProjetos().getProjeto(request.vars.ID_PROJETO)
    perguntas = db(db.avaliacao_perguntas.edicao == session.edicao.id).select()
    form = FormPerguntas(perguntas).formAvaliacao()

    if form.process().accepted:
        avaliacao = db.avaliacao.insert(
            id_projeto=request.vars.ID_PROJETO,
            avaliador=session.auth.user.id,
            dt_envio=datetime.now(),
            is_deferido=False,
            observacao=form.vars.observacao
        )

        respostas = form.vars.copy()
        del respostas['observacao']
        if avaliacao:
            for i in respostas:
                db.avaliacao_respostas.insert(
                    pergunta=i,
                    avaliacao=avaliacao,
                    resposta=True if respostas[i] else False
                )

            SIEProjetos().avaliarProjeto(request.vars.ID_PROJETO, 9)

            try:
                coordenador = current.api.performGETRequest(
                "V_SERVIDORES_EMAIL",
                {
                    "ID_PESSOA": SIEProjetos().getCoordenador(request.vars.ID_PROJETO)["ID_PESSOA"]
                }
                ).content[0]
                email = MailAvaliacao(coordenador)
                email.sendConfirmationEmail()
            except Exception:
                session.flash = "Não foi possível enviar email de confirmação."

            session.flash = "Projeto #%d avaliado com sucesso" % projeto['ID_PROJETO']
            redirect(URL("adm", "avaliacao"))
        else:
            response.flash = "Não foi possível salvar a avaliação. Tente novamente."

    return dict(projeto=projeto, form=form)


@auth.requires(auth.has_membership('PROGRAD') or auth.has_membership('DTIC'))
def deferidos():
    try:
        projetos = api.performGETRequest("V_PROJETOS_DADOS", {
            "DESCRICAO": "Ensino",
            "ORDERBY": "DT_REGISTRO",
            "SORT": "DESC",
            "SITUACAO": "Em andamento",
            "LMIN": 0,
            "LMAX": 5000
        }, cached=360)
        avaliador = Avaliacao()

        for p in projetos.content:
            p.update({"AVALIADOR": avaliador.getAvaliador(p["ID_PROJETO"])})

        table = TableDeferimento(projetos.content)
        form = table.printTable()

        if form.process().accepted:
            @auth.requires(auth.has_membership('admin') or auth.has_membership('DTIC'))
            def __removerProjeto(ID_PROJETO):
                try:
                    SIEProjetos().removerProjeto(ID_PROJETO)
                    for p in projetos.content:
                        if p['ID_PROJETO'] == int(ID_PROJETO):
                            projetos.content.remove(p)
                except Exception as e:
                    response.flash = e.message

            '''
            Essa verificação é necessária pela forma como o HTML trabalha com checkboxes. Se apenas um item for
            selecionado, a variável será uma string, caso vários items sejam selecionados, a variável será uma lista.
            Não faz o mínimo sentido a forma como isso foi implementado, visto que uma um item poderia ser resprentado
            como uma lista de apenas um elemento.

            Ref: http://comments.gmane.org/gmane.comp.python.web2py/13251
            '''
            if isinstance(form.vars.toDelete, list):
                for ID_PROJETO in form.vars.toDelete:
                    __removerProjeto(ID_PROJETO)
            else:
                __removerProjeto(form.vars.toDelete)
            response.flash = "Projetos removidos com sucesso"


        return dict(tableForm=form)
    except AttributeError:
        return dict(tableForm="Nenhum projeto deferido até o momento.")


@auth.requires(auth.has_membership('PROGRAD') or auth.has_membership('DTIC'))
def indeferidos():
    try:
        projetos = api.performGETRequest("V_PROJETOS_DADOS", {
            "DESCRICAO": "Ensino",
            "ORDERBY": "DT_REGISTRO",
            "SITUACAO": "Indeferido",
            "SORT": "DESC",
            "LMIN": 0,
            "LMAX": 5000
        })
        avaliador = Avaliacao()

        for p in projetos.content:
            p.update({"AVALIADOR": avaliador.getAvaliador(p["ID_PROJETO"])})

        table = TableDeferimento(projetos.content)
        form = table.printTable()

        if form.process().accepted:
            @auth.requires(auth.has_membership('admin') or auth.has_membership('DTIC'))
            def __removerProjeto(ID_PROJETO):
                try:
                    SIEProjetos().removerProjeto(ID_PROJETO)
                    for p in projetos.content:
                        if p['ID_PROJETO'] == int(ID_PROJETO):
                            projetos.content.remove(p)
                except Exception as e:
                    response.flash = e.message

            '''
            Essa verificação é necessária pela forma como o HTML trabalha com checkboxes. Se apenas um item for
            selecionado, a variável será uma string, caso vários items sejam selecionados, a variável será uma lista.
            Não faz o mínimo sentido a forma como isso foi implementado, visto que uma um item poderia ser resprentado
            como uma lista de apenas um elemento.

            Ref: http://comments.gmane.org/gmane.comp.python.web2py/13251
            '''
            if isinstance(form.vars.toDelete, list):
                for ID_PROJETO in form.vars.toDelete:
                    __removerProjeto(ID_PROJETO)
            else:
                __removerProjeto(form.vars.toDelete)

        return dict(tableForm=form)
    except AttributeError:
        return dict(tableForm="Nenhum projeto indeferido.")


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)
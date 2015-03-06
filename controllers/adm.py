# coding=utf-8
from datetime import datetime

from relatorios import Deferimento, salvarCSV
from avaliacao import Avaliacao
from mail import MailAvaliacao
from forms import FormPerguntas
from unirio.api.apiresult import APIException
from sie.SIEProjetos import SIEProjetos, SIEParticipantesProjs
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


@auth.requires(auth.has_membership('PROGRAD') or auth.has_membership('DTIC'))
def cadastro_perguntas():
    db.avaliacao_perguntas.id.readable = False
    grid = SQLFORM.grid(
        query=db.avaliacao_perguntas.edicao == db.edicao.id,
        fields=(db.edicao.nome, db.avaliacao_perguntas.pergunta),
        field_id=db.avaliacao_perguntas.id,
        orderby=db.edicao.nome,
        deletable=False,
        csv=False
    )
    return dict(grid=grid)


@auth.requires((auth.has_membership('PROGRAD') or auth.has_membership('DTIC')) and edicao.requires_edicao())
def avaliacao():
    try:
        projetos = api.performGETRequest("V_PROJETOS_DADOS", {
            "ID_CLASSIFICACAO": 40161,  # Projeto de ensino
            "DT_INICIAL": session.edicao.dt_inicial_projeto,
            "LMIN": 0,
            "LMAX": 99999
        }).content
    except ValueError:
        projetos = []

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


@auth.requires(auth.has_permission('alterarSituacao'))
def alterarSituacao():
    try:
        r = api.performPUTRequest("PROJETOS", {
            "ID_PROJETO": request.vars.ID_PROJETO,
            "SITUACAO_ITEM": request.vars.SITUACAO_ITEM
        })
        if r.affectedRows:
            return T('Resource updated')
    except APIException:
        return T('Unable to update')


@auth.requires(auth.has_membership('PROGRAD') or auth.has_membership('DTIC'))
def avaliacaoPerguntas():
    # TODO deveria ser um decorator?
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
                coordenador = api.performGETRequest(
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


@auth.requires(auth.has_membership('PROGRAD') or auth.has_membership('DTIC') and edicao.requires_edicao())
def deferidos():
    try:
        relatorio = Deferimento(session.edicao)
        projetos = relatorio.projetosDeferidos()

        form = TableDeferimento(projetos).printTable()

        if form.process().accepted:
            @auth.requires(auth.has_membership('admin') or auth.has_membership('DTIC'))
            def __removerProjeto(ID_PROJETO):
                try:
                    SIEProjetos().removerProjeto(ID_PROJETO)
                    db.log_admin.insert(acao='delete', tablename='PROJETOS', uid=ID_PROJETO, user_id=auth.user_id,
                                        dt_alteracao=datetime.now())
                    for p in projetos.content:
                        if p['ID_PROJETO'] == int(ID_PROJETO):
                            projetos.content.remove(p)
                except Exception as e:
                    response.flash = e.message

            '''
            Essa verificação é necessária pela forma como o HTML trabalha com checkboxes. Se apenas um item for
            selecionado, a variável será uma string, caso vários items sejam selecionados, a variável será uma lista.

            Ref: http://comments.gmane.org/gmane.comp.python.web2py/13251
            '''
            if isinstance(form.vars.toDelete, list):
                for ID_PROJETO in form.vars.toDelete:
                    __removerProjeto(ID_PROJETO)
            else:
                __removerProjeto(form.vars.toDelete)
            response.flash = "Projetos removidos com sucesso"

        return dict(
            relatorio=salvarCSV(projetos, "deferidos"),
            tableForm=form,
            projetos=projetos,
            bolsasCount=relatorio.bolsasCount
        )
    except (AttributeError, ValueError) as e:
        return dict(projetos=None)


@auth.requires(auth.has_membership('PROGRAD') or auth.has_membership('DTIC') and edicao.requires_edicao())
def indeferidos():
    try:
        relatorio = Deferimento(session.edicao)
        projetos = relatorio.projetosIndeferidos()

        form = TableDeferimento(projetos).printTable()

        if form.process().accepted:
            @auth.requires(auth.has_membership('admin') or auth.has_membership('DTIC'))
            def __removerProjeto(ID_PROJETO):
                try:
                    SIEProjetos().removerProjeto(ID_PROJETO)
                    db.log_admin.insert(acao='delete', tablename='PROJETOS', uid=ID_PROJETO, user_id=auth.user_id,
                                        dt_alteracao=datetime.now())
                    for p in projetos.content:
                        if p['ID_PROJETO'] == int(ID_PROJETO):
                            projetos.content.remove(p)
                except Exception as e:
                    response.flash = e.message

            if isinstance(form.vars.toDelete, list):
                for ID_PROJETO in form.vars.toDelete:
                    __removerProjeto(ID_PROJETO)
            else:
                __removerProjeto(form.vars.toDelete)
            response.flash = "Projetos removidos com sucesso"

        return dict(
            relatorio=salvarCSV(projetos, "indeferidos"),
            tableForm=form,
            projetos=projetos,
            bolsasCount=relatorio.bolsasCount
        )
    except (AttributeError, ValueError):
        return dict(projetos=None)


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


@auth.requires_permission('alterarBolsas')
def ajaxAlterarBolsas():
    ID_PROJETO = int(request.vars.keys()[0])
    quantidade_bolsas = int(request.vars.values()[0])

    bolsistas = SIEParticipantesProjs().getParticipantes({
        "ID_PROJETO": request.vars.ID_PROJETO,
        "FUNCAO_ITEM": 3  # Bolsista
    })

    if not proj.registroBolsistaAberto(ID_PROJETO):
        if not bolsistas or len(bolsistas) < quantidade_bolsas:
            valor_anterior = db(db.bolsas.id_projeto == ID_PROJETO).select().first().quantidade_bolsas

            db(db.bolsas.id_projeto == ID_PROJETO).update(quantidade_bolsas=quantidade_bolsas)
            db.log_admin.insert(
                acao='update',
                valores=valor_anterior,
                tablename='bolsas',
                colname='quantidade_bolsas',
                uid=ID_PROJETO,
                user_id=auth.user_id,
                dt_alteracao=datetime.now()
            )
        else:
            session.flash = "Não foi possível alterar a quantidade bolsas: Não é possível remover uma bolsa já alocada a um participante."
    else:
        session.flash = "Não foi possível alterar a quantidade bolsas: Registro de bolsistas aberto."
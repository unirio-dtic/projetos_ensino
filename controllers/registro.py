# -*- coding: utf-8 -*-
from sie.SIEFuncionarios import SIEFuncionarioID
from sie.SIEProjetos import SIEParticipantesProjs


def requires_edicao(f):
    if not session.edicao:
        session.flash = 'Você precisa selecionar uma edição'
        redirect(URL('registro', 'index'))
    return f


def index():
    from forms import FormEdicoes
    session.edicao = None

    form = FormEdicoes().form()

    if form.process().accepted:
        session.edicao = db(db.edicao.id == form.vars.edicao).select().first()
        try:
            session.funcionario = SIEFuncionarioID("12330675755").getFuncionarioIDs()
        except ValueError:
            session.flash = "Seus dados não foram encontrados. É possível que você não esteja " \
                            "autorizado a acessar este recurso."
            redirect(URL("default", "index"))

        redirect(URL('registro', 'registro'))

    return dict(form=form)


def registro():
    from sie.SIEProjetos import SIEProjetos, SIEClassificacoesPrj, SIECursosDisciplinas
    from forms import FormProjetos
    from operator import itemgetter

    classificacoes = SIEClassificacoesPrj().getClassificacoesPrj()
    cursos = SIECursosDisciplinas()
    # distinct
    cursos = {v['ID_CURSO']:v for v in cursos.getCursos()}.values()
    # order by
    cursos = sorted(cursos, key=itemgetter('NOME_CURSO'))
    form = FormProjetos(classificacoes, cursos).formRegistro()
    if form.process().accepted:
        projetos = SIEProjetos()
        novoProjeto = projetos.salvarProjeto(form.vars, session.funcionario)

        participantesProj = SIEParticipantesProjs()
        novoParticipante = participantesProj.criarParticipante(
            novoProjeto["ID_PROJETO"],
            session.funcionario
        )
    else:
        pass

    return dict(form=form)



# -*- coding: utf-8 -*-
from sie.SIEFuncionarios import SIEFuncionarioID
from sie.SIEProjetos import SIEParticipantesProjs, SIECursosDisciplinas


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
    from sie.SIEProjetos import SIEProjetos, SIEClassificacoesPrj
    from forms import FormProjetos
    from operator import itemgetter

    classificacoes = SIEClassificacoesPrj().getClassificacoesPrj()
    cursos = SIECursosDisciplinas().getCursos()
    # distinct
    cursos = {v['ID_CURSO']:v for v in cursos}.values()
    # order by
    cursos = sorted(cursos, key=itemgetter('NOME_CURSO'))
    cursos.insert(0, {'ID_CURSO': '', 'NOME_CURSO': 'Selecione'})
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

def getDisciplinasHTMLOptions():
    return SIECursosDisciplinas().getDisciplinasHTMLOptions(request.vars.ID_CURSO, session.edicao.disciplinas_obrigatorias)
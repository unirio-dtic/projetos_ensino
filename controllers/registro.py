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
    from sie.SIEProjetos import SIEProjetos, SIEClassificacoesPrj, SIEClassifProjetos, SIEOrgaosProjetos, SIEArquivosProj
    from forms import FormProjetos

    classificacoes = cache.ram(
        'classificacoes',
        lambda: SIEClassificacoesPrj().getClassificacoesPrj(1, 1),
        time_expire=86400  # Um dia 86400
    )
    cursos = cache.ram(
        'cursos',
        lambda: SIECursosDisciplinas().getCursos(),
        time_expire=86400  # Um dia
    )

    form = FormProjetos(classificacoes, cursos).formRegistro()
    if form.process().accepted:
        projeto = form.vars.copy()
        del projeto["CONTEUDO_ARQUIVO"]
        novoProjeto = SIEProjetos().salvarProjeto(projeto, session.funcionario)

        SIEArquivosProj().salvarArquivo(form.vars.CONTEUDO_ARQUIVO, novoProjeto, session.funcionario)
        # A classificacao de um projeto de ensino permite apenas uma diciplina
        classificacao = SIEClassificacoesPrj().getClassificacoesPrj(41, form.vars.COD_DISCIPLINA)[0]

        SIEClassifProjetos().criarClassifProjetos(novoProjeto["ID_PROJETO"], classificacao["ID_CLASSIFICACAO"])

        SIEOrgaosProjetos().criarOrgaosProjetos(novoProjeto, form.vars.ID_UNIDADE)

        participantesProj = SIEParticipantesProjs()
        novoParticipante = participantesProj.criarParticipante(
            novoProjeto["ID_PROJETO"],
            session.funcionario
        )
    else:
        pass

    return dict(form=form)


def getDisciplinasHTMLOptions():
    disciplinas = SIECursosDisciplinas().getDisciplinas(request.vars.ID_CURSO, session.edicao.disciplinas_obrigatorias)
    options = [str(OPTION(disciplina["NOME_DISCIPLINA"], _value=disciplina["COD_DISCIPLINA"])) for disciplina in
               disciplinas]
    return str(options)

def getIdUnidade():
    return SIECursosDisciplinas().getIdUnidade(request.vars.ID_CURSO)
# -*- coding: utf-8 -*-
from cgi import FieldStorage

from sie.SIEProjetos import SIEParticipantesProjs, SIECursosDisciplinas


@auth.requires_login()
def registro():
    from sie.SIEProjetos import SIEProjetos, SIEClassificacoesPrj, SIEClassifProjetos, SIEOrgaosProjetos, SIEArquivosProj
    from forms import FormProjetos

    if not current.session.edicao:
        redirect(URL("default", "edicoes"))

    classificacoes = SIEClassificacoesPrj().getClassificacoesPrj(1, 1)
    cursos = SIECursosDisciplinas().getCursos()

    form = FormProjetos(classificacoes, cursos).formRegistro()
    if form.process().accepted:
        projeto = {k: v for k, v in form.vars.iteritems() if not isinstance(v, FieldStorage)}
        novoProjeto = SIEProjetos().salvarProjeto(projeto, session.funcionario)

        db.bolsas.insert(
            id_projeto=novoProjeto["ID_PROJETO"],
            quantidade_bolsas=novoProjeto["quantidade_bolsas"]
        )

        #TODO "embelezar" essa parte
        SIEArquivosProj().salvarArquivo(form.vars.CONTEUDO_ARQUIVO1, novoProjeto, session.funcionario, 1)
        SIEArquivosProj().salvarArquivo(form.vars.CONTEUDO_ARQUIVO5, novoProjeto, session.funcionario, 5)
        if form.vars.CONTEUDO_ARQUIVO14:
            SIEArquivosProj().salvarArquivo(form.vars.CONTEUDO_ARQUIVO14, novoProjeto, session.funcionario, 14)
        if form.vars.CONTEUDO_ARQUIVO17:
            SIEArquivosProj().salvarArquivo(form.vars.CONTEUDO_ARQUIVO17, novoProjeto, session.funcionario, 17)

        classificacao = SIEClassificacoesPrj().getClassificacoesPrj(41, form.vars.COD_DISCIPLINA)[0]

        SIEClassifProjetos().criarClassifProjetos(novoProjeto["ID_PROJETO"], classificacao["ID_CLASSIFICACAO"])

        SIEOrgaosProjetos().criarOrgaosProjetos(novoProjeto, form.vars.ID_UNIDADE)

        participantesProj = SIEParticipantesProjs()
        novoParticipante = participantesProj.criarParticipante(
            novoProjeto["ID_PROJETO"],
            session.funcionario
        )

        redirect(URL('consulta', 'index'))
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
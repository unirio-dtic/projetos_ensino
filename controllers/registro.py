# -*- coding: utf-8 -*-
from cgi import FieldStorage

from sie.SIEProjetos import SIEParticipantesProjs, SIECursosDisciplinas
from sie.SIEProjetos import SIEProjetos, SIEClassificacoesPrj, SIEClassifProjetos, SIEOrgaosProjetos, SIEArquivosProj
from forms import FormProjetos, FormArquivos


@auth.requires_login()
def registro():
    if not (current.session.edicao and current.session.funcionario):
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

        classificacao = SIEClassificacoesPrj().getClassificacoesPrj(41, form.vars.COD_DISCIPLINA)[0]

        SIEClassifProjetos().criarClassifProjetos(novoProjeto["ID_PROJETO"], classificacao["ID_CLASSIFICACAO"])

        SIEOrgaosProjetos().criarOrgaosProjetos(novoProjeto, form.vars.ID_UNIDADE)

        participantesProj = SIEParticipantesProjs()
        novoParticipante = participantesProj.criarParticipante(
            novoProjeto["ID_PROJETO"],
            session.funcionario
        )
        session.projeto = novoProjeto

        redirect(URL('registro', 'arquivo_projeto'))

    return dict(form=form)


def arquivo_projeto():
    response.title = 'Registro - Envio de arquivos 1/4'
    response.view = 'registro/envioArquivo.html'
    progress = 20
    form = FormArquivos().formArquivoProjeto()

    # TODO deveria ser um decorator
    if not session.projeto:
        redirect(URL("registro", "registro"))

    if form.process().accepted:
        try:
            SIEArquivosProj().salvarArquivo(form.vars.CONTEUDO_ARQUIVO, session.projeto, session.funcionario, 1)
            redirect(URL("registro", "ata_departamento"))
        except IOError as e:
            if e.errno == 36:
                response.flash = "Não foi possível salvar o arquivo. Nome muito longo."
    return dict(locals())


def ata_departamento():
    response.title = 'Registro - Envio de arquivos 2/4'
    response.view = 'registro/envioArquivo.html'
    progress = 40
    form = FormArquivos().formArquivoAta()

    # TODO deveria ser um decorator
    if not session.projeto:
        redirect(URL("registro", "registro"))

    if form.process().accepted:
        try:
            SIEArquivosProj().salvarArquivo(form.vars.CONTEUDO_ARQUIVO, session.projeto, session.funcionario, 5)
            redirect(URL("registro", "relatorio_docente"))
        except IOError as e:
            if e.errno == 36:
                response.flash = "Não foi possível salvar o arquivo. Nome muito longo."
    return dict(locals())


def relatorio_docente():
    response.title = 'Registro - Envio de arquivos 3/4'
    response.view = 'registro/envioArquivo.html'
    progress = 60
    form = FormArquivos().formArquivoRelatioDocente()

    # TODO deveria ser um decorator
    if not session.projeto:
        redirect(URL("registro", "registro"))

    if form.process().accepted:
        try:
            if isinstance(form.vars['CONTEUDO_ARQUIVO'], FieldStorage):
                SIEArquivosProj().salvarArquivo(form.vars.CONTEUDO_ARQUIVO, session.projeto, session.funcionario, 14)
            redirect(URL("registro", "relatorio_bolsista"))
        except IOError as e:
            if e.errno == 36:
                response.flash = "Não foi possível salvar o arquivo. Nome muito longo."
    return dict(locals())


def relatorio_bolsista():
    response.title = 'Registro - Envio de arquivos 4/4'
    response.view = 'registro/envioArquivo.html'
    progress = 80
    form = FormArquivos().formArquivoRelatorioBolsista()

    # TODO deveria ser um decorator'
    if not session.projeto:
        redirect(URL("registro", "registro"))

    if form.process().accepted:
        try:
            if isinstance(form.vars['CONTEUDO_ARQUIVO'], FieldStorage):
                SIEArquivosProj().salvarArquivo(form.vars.CONTEUDO_ARQUIVO, session.projeto, session.funcionario, 17)
            session.flash = "Envio finalizado com sucesso"
            session.projeto = None
            redirect(URL("consulta", "index"))
        except IOError as e:
            if e.errno == 36:
                response.flash = "Não foi possível salvar o arquivo. Nome muito longo."

    return dict(locals())


def getDisciplinasHTMLOptions():
    disciplinas = SIECursosDisciplinas().getDisciplinas(request.vars.ID_CURSO, session.edicao.disciplinas_obrigatorias)
    options = [str(OPTION(disciplina["NOME_DISCIPLINA"].encode('latin1'), _value=disciplina["COD_DISCIPLINA"])) for disciplina in
               disciplinas]
    return options


def getIdUnidade():
    return SIECursosDisciplinas().getIdUnidade(request.vars.ID_CURSO)
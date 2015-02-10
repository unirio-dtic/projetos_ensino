# -*- coding: utf-8 -*-
from cgi import FieldStorage
from itertools import izip_longest
from sie.SIEAlunos import SIEAlunos
from sie.SIEProjetos import SIEParticipantesProjs, SIECursosDisciplinas
from sie.SIEProjetos import SIEProjetos, SIEClassificacoesPrj, SIEClassifProjetos, SIEOrgaosProjetos, SIEArquivosProj
from forms import FormProjetos, FormArquivos, FormBolsista


@auth.requires(edicao.requires_edicao() and pessoa.isFuncionario())
def registro():
    if not edicao.isValidEdicaoForRegistro(session.edicao):
        session.flash = "Edição não está aberta para registro"
        redirect(URL('default', 'edicoes'))

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


@auth.requires(projeto.requires_projeto())
def arquivo_projeto():
    response.title = 'Registro - Envio de arquivos 1/4'
    response.view = 'registro/envioArquivo.html'
    progress = 20
    form = FormArquivos().formArquivoProjeto()

    if form.process().accepted:
        try:
            SIEArquivosProj().salvarArquivo(form.vars.CONTEUDO_ARQUIVO, session.projeto, session.funcionario, 1)
            redirect(URL("registro", "ata_departamento"))
        except IOError as e:
            if e.errno == 36:
                response.flash = "Não foi possível salvar o arquivo. Nome muito longo."
    return dict(locals())


@auth.requires(projeto.requires_projeto())
def ata_departamento():
    response.title = 'Registro - Envio de arquivos 2/4'
    response.view = 'registro/envioArquivo.html'
    progress = 40
    form = FormArquivos().formArquivoAta()

    if form.process().accepted:
        try:
            SIEArquivosProj().salvarArquivo(form.vars.CONTEUDO_ARQUIVO, session.projeto, session.funcionario, 5)
            redirect(URL("registro", "relatorio_docente"))
        except IOError as e:
            if e.errno == 36:
                response.flash = "Não foi possível salvar o arquivo. Nome muito longo."
    return dict(locals())


@auth.requires(projeto.requires_projeto())
def relatorio_docente():
    response.title = 'Registro - Envio de arquivos 3/4'
    response.view = 'registro/envioArquivo.html'
    progress = 60
    form = FormArquivos().formArquivoRelatioDocente()

    if form.process().accepted:
        try:
            if isinstance(form.vars['CONTEUDO_ARQUIVO'], FieldStorage):
                SIEArquivosProj().salvarArquivo(form.vars.CONTEUDO_ARQUIVO, session.projeto, session.funcionario, 14)
            redirect(URL("registro", "relatorio_bolsista"))
        except IOError as e:
            if e.errno == 36:
                response.flash = "Não foi possível salvar o arquivo. Nome muito longo."
    return dict(locals())


@auth.requires(projeto.requires_projeto())
def relatorio_bolsista():
    response.title = 'Registro - Envio de arquivos 4/4'
    response.view = 'registro/envioArquivo.html'
    progress = 80
    form = FormArquivos().formArquivoRelatorioBolsista()

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
    options = [str(OPTION(disciplina["NOME_DISCIPLINA"], _value=disciplina["COD_DISCIPLINA"])) for disciplina in
               disciplinas]
    return options


def getIdUnidade():
    return SIECursosDisciplinas().getIdUnidade(request.vars.ID_CURSO)


@auth.requires(edicao.requires_edicao() and pessoa.isAluno())
def bolsista():
    projeto = SIEProjetos().getProjetoDados(request.vars.ID_PROJETO)
    try:
        alunosPossiveis = api.performGETRequest(
            "V_NOTAS_FINAIS_ALUNOS_DISCIPLINAS",
            {
                "COD_ATIV_CURRIC": projeto['COD_DISCIPLINA'],
                "LMIN": 0,
                "LMAX": 2000,
                "MEDIA_FINAL_MIN": 7.0,
                "FORMA_EVASAO_ITEM": 1,
                "ORDERBY": "NOME_PESSOA"
            },
            ["ID_PESSOA", "ID_ALUNO", "MATR_ALUNO", "NOME_PESSOA", "MEDIA_FINAL", "NOME_PAI", "NOME_MAE", "SEXO",
             "NOME_CIDADE", "DESCR_BAIRRO", "FOTO", "ANO", "PERIODO_ITEM"]
        ).content

        apiAlunos = SIEAlunos()

        for aluno in alunosPossiveis:
            aluno.update({"CRA": apiAlunos.getCRA(aluno['ID_ALUNO'])})

        def grouper(n, iterable):
            """
            Usado para agrupar os alunos em grupos de 3 para poder usar corretamente bs`s row-fluid

            ref: http://stackoverflow.com/questions/1624883/alternative-way-to-split-a-list-into-groups-of-n
            ref: http://stackoverflow.com/questions/15869169/bootstrap-thumbnails-not-stacking-properly
            grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx
            """
            args = [iter(iterable)] * n
            return izip_longest(*args)
        groups = list(grouper(3, alunosPossiveis))
    except ValueError:
        groups = []
    return dict(
        projeto=projeto,
        groups=groups
    )
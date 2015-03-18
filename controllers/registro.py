# -*- coding: utf-8 -*-
from cgi import FieldStorage
from itertools import izip_longest
from sie.SIEAlunos import SIEAlunos
from sie.SIEProjetos import SIEParticipantesProjs, SIECursosDisciplinas
from sie.SIEProjetos import SIEProjetos, SIEClassificacoesPrj, SIEClassifProjetos, SIEOrgaosProjetos, SIEArquivosProj
from forms import FormProjetos, FormArquivos, FormBolsista


@auth.requires(lambda: edicao.requires_edicao() and pessoa.isFuncionario())
def registro():
    if not edicao.isValidEdicaoForRegistro(session.edicao):
        session.flash = "Edição não está aberta para registro"
        redirect(URL('default', 'edicoes'))

    classificacoes = SIEClassificacoesPrj().getClassificacoesPrj(1, 1)
    cursos = SIECursosDisciplinas().getCursosGraduacao()

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

        SIEOrgaosProjetos().criarOrgaosProjetos(novoProjeto, SIECursosDisciplinas().getIdUnidade(request.vars.ID_CURSO))

        SIEParticipantesProjs().criarParticipanteCoordenador(novoProjeto["ID_PROJETO"], session.funcionario)

        session.projeto = novoProjeto

        redirect(URL('registro', 'arquivo_projeto'))

    return dict(form=form)


@auth.requires(lambda: proj.requires_projeto())
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


@auth.requires(lambda: proj.requires_projeto())
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


@auth.requires(lambda: proj.requires_projeto())
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


@auth.requires(lambda: proj.requires_projeto())
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


def ajaxDisciplinas():
    def _disciplinas(ID_CURSO):
        disciplinas = SIECursosDisciplinas().getDisciplinas(ID_CURSO, session.edicao.disciplinas_obrigatorias)
        for disciplina in disciplinas:
            yield str(OPTION(disciplina["NOME_DISCIPLINA"], _value=disciplina["COD_DISCIPLINA"]))

    return _disciplinas(request.vars.ID_CURSO)


@auth.requires(lambda: edicao.requires_edicao() and proj.isCoordenador())
def bolsista():
    ID_PROJETO = request.vars.ID_PROJETO
    if not proj.registroBolsistaAberto(session.edicao):
        session.flash = 'O período de cadastro de bolsistas não está aberto.'
        redirect(URL('consulta', 'aprovados'))

    projeto = SIEProjetos().getProjetoDados(ID_PROJETO)
    bolsas = db(db.bolsas.id_projeto == ID_PROJETO).select(cache=(cache.ram, 600)).first().quantidade_bolsas

    try:
        session.alunosPossiveis = None
        alunosPossiveis = api.performGETRequest(
            "V_NOTAS_FINAIS_ALUNOS_DISCIPLINAS",
            {
                "COD_ATIV_CURRIC": projeto['COD_DISCIPLINA'],
                "LMIN": 0,
                "LMAX": 2000,
                "SITUACAO_ITEM": 1,         # Aprovado
                "FORMA_EVASAO_ITEM": 1,     # Sem evasão
                "ORDERBY": "NOME_PESSOA"
            },
            ["ID_PESSOA", "ID_ALUNO", "MATR_ALUNO", "NOME_PESSOA", "MEDIA_FINAL", "SEXO",
             "NOME_CIDADE", "DESCR_BAIRRO", "DESCR_MAIL", "FOTO", "ANO"]
        ).content

        apiAlunos = SIEAlunos()
        cras = apiAlunos.getCRAAlunos(tuple(a['ID_ALUNO'] for a in alunosPossiveis))
        map(lambda a: a.update(cras[a['ID_ALUNO']]), alunosPossiveis)
        session.alunosPossiveis = alunosPossiveis[:]

        participantes = SIEParticipantesProjs().getParticipantes({
            'ID_PROJETO': request.vars.ID_PROJETO,
            'FUNCAO_ITEM': 3,    # Bolsista
            'SITUACAO': "A"
        })

        def grouper(n, iterable):
            """
            Usado para agrupar os alunos em grupos de 3 para poder usar corretamente bs`s row-fluid
            grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx
            """
            args = [iter(iterable)] * n
            return izip_longest(*args)

        if participantes:
            def __bolsistas():
                alunos = []
                for p in participantes:
                    for a in alunosPossiveis:
                        if a['ID_PESSOA'] == p['ID_PESSOA']:
                            aluno = a.copy()
                            aluno.update(p)
                            alunos.append(aluno)
                return alunos

            bolsistas = __bolsistas()
            participantesBolsistas = [a['ID_CURSO_ALUNO'] for a in bolsistas]

            # Remove os alunos que já foram selecionados como bolsistas
            alunosPossiveis[:] = [a for a in alunosPossiveis if a['ID_CURSO_ALUNO'] not in participantesBolsistas]
        else:
            bolsistas = None
            participantesBolsistas = None

        return dict(
            bolsas=bolsas,
            bolsistas=bolsistas,
            participantesBolsistas=participantesBolsistas,
            projeto=projeto,
            groups=list(grouper(3, alunosPossiveis)),
            podeCadastrar=not bolsistas or len(participantesBolsistas) < bolsas
        )
    except ValueError:
        return dict(groups=[])
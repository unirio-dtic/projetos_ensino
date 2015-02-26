# coding=utf-8
from sie.SIEBancos import SIEAgencias
from forms import FormBolsista
from sie.SIEBolsistas import SIEBolsistas
from sie.SIEProjetos import SIEParticipantesProjs, SIEProjetos


@auth.requires(pessoa.isAluno())
def dados():
    participacoes = SIEParticipantesProjs().getParticipacoes(session.aluno, {'FUNCAO_ITEM': 3})

    if not participacoes:
        session.flash = 'Você não foi selecionado como bolsista para nenhum projeto.'
        redirect(URL('default', 'index'))

    def __getter(participacoes):
        p = SIEProjetos()
        b = SIEBolsistas()
        for part in participacoes:
            yield p.getProjeto(part['ID_PROJETO'])
            yield b.getBolsista(part['ID_BOLSISTA'])

    projetos, bolsas = __getter(participacoes)

    form = FormBolsista().formCadastroBolsista()

    if form.process().accepted:
        for bolsa in bolsas:
            SIEBolsistas().atualizarDadosBancarios(bolsa['ID_BOLSISTA'], form.vars)

    return dict(locals())


@auth.requires(pessoa.isFuncionario() and proj.isCoordenador() and edicao.requires_edicao())
def ajaxCadastrarParticipante():
    bolsas = db(db.bolsas.id_projeto == request.vars.ID_PROJETO).select().first().quantidade_bolsas

    if not bolsas:
        return dict(success=False)

    bolsistas = SIEParticipantesProjs().getParticipantes({
        "ID_PROJETO": request.vars.ID_PROJETO,
        "FUNCAO_ITEM": 3
    })

    if not bolsistas or len(bolsistas) < bolsas:
        for a in session.alunosPossiveis:
            if a['ID_CURSO_ALUNO'] == int(request.vars.ID_CURSO_ALUNO):
                aluno = a
                break

        if aluno:
            projeto = SIEProjetos().getProjetoDados(request.vars.ID_PROJETO)
            SIEParticipantesProjs().criarParticipanteBolsista(projeto, aluno, session.edicao)
            return dict(success=True)


def ajaxCarregarAgencias():
    agencia = lambda ag: str(OPTION("%s-%s  %s" % (ag['COD_AGENCIA'], ag['DV_AGENCIA'], ag['NOME_AGENCIA']), _value=a['ID_AGENCIA']))
    for a in SIEAgencias().getAgenciasDeBanco(request.vars.ID_BANCO):
        yield agencia(a)
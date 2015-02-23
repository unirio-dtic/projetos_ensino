# coding=utf-8
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

    projetos, bolsistas = __getter(participacoes)

    form = FormBolsista().formCadastroBolsista()

    if form.process().accepted:
        # Atualizar entrada na tabela de bolsista para os dados bancários do form
        pass

    return dict(locals())


@auth.requires(pessoa.isFuncionario() and proj.isCoordenador())
def ajaxCadastrarParticipante():
    bolsas = db(db.bolsas.id_projeto == request.vars.ID_PROJETO).select().first().quantidade_bolsas

    if not bolsas:
        return dict(success=False)

    bolsistas = SIEParticipantesProjs().getParticipantes({
        "ID_PROJETO": request.vars.ID_PROJETO,
        "FUNCAO_ITEM": 3
    })

    if not bolsistas or len(bolsistas) < bolsas:
        aluno = (aluno for aluno in session.alunosPossiveis if aluno['ID_CURSO_ALUNO'] == request.vars.ID_CURSO_ALUNO)
        if aluno:
            SIEParticipantesProjs().criarParticipanteBolsista(request.vars.ID_PROJETO, aluno)
            return dict(success=True)
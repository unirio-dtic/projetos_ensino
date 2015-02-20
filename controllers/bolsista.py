# coding=utf-8
from sie.SIEProjetos import SIEParticipantesProjs


@auth.requires(pessoa.isAluno())
def dados():
    session.flash = 'Indisponível no momento.'
    redirect(URL('default', 'index'))


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
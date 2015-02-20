# coding=utf-8
from sie.SIEProjetos import SIEParticipantesProjs


@auth.requires(pessoa.isAluno())
def dados():
    session.flash = 'Indisponível no momento.'
    redirect(URL('default', 'index'))


@auth.requires(pessoa.isFuncionario())
def ajaxCadastrarParticipante():
    SIEParticipantesProjs().criarParticipanteAluno(request.vars.ID_PROJETO)
    return dict()
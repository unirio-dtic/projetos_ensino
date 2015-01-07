from sie.SIEProjetos import SIEParticipantesProjs, SIEProjetos


def index():
    session.funcionario["ID_PESSOA"] = 49

    participacoes = SIEParticipantesProjs().getParticipacoes(session.funcionario)
    projetos = [SIEProjetos().getProjeto(projeto["ID_PROJETO"]) for projeto in participacoes.content]

    return dict(
        particicacoes=participacoes.content,
        projetos=projetos
    )
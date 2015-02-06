from sie.SIEProjetos import SIEProjetos


def index():
    projeto = SIEProjetos().getProjetoDados(request.vars.ID_PROJETO)
    return dict(locals())


def bolsistas():
    alunos = api.performGETRequest("ALUNOS", {"LMIN": 0, "LMAX": 99000}, cached=86400)
    alunosComFotos = [aluno for aluno in alunos.content if aluno['FOTO']]
    return dict(locals())
# coding=utf-8
from mail import MailBolsista
from sie.SIEBancos import SIEAgencias
from forms import FormBolsista
from sie.SIEBolsistas import SIEBolsistas
from sie.SIEProjetos import SIEParticipantesProjs, SIEProjetos


@auth.requires(pessoa.isAluno())
def dados():
    # Todas as participações como bolsista que estejam ativas
    participacoes = SIEParticipantesProjs().getParticipacoes(session.aluno, {'FUNCAO_ITEM': 3, 'SITUACAO': 'A'})

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
        for bolsa in bolsas.content:
            SIEBolsistas().atualizarDadosBancarios(bolsa['ID_BOLSISTA'], form.vars)

    return dict(projetos=projetos, bolsas=bolsas, form=form)


@auth.requires(proj.isCoordenador() and proj.registroBolsistaAberto(request.vars.ID_PROJETO))
def ajaxCadastrarParticipante():
    bolsas = db(db.bolsas.id_projeto == request.vars.ID_PROJETO).select(cache=(cache.ram, 600)).first().quantidade_bolsas

    if not bolsas:
        return dict(success=False, msg="Projeto não possui bolsas.")

    bolsistas = SIEParticipantesProjs().getParticipantes({
        "ID_PROJETO": request.vars.ID_PROJETO,
        "FUNCAO_ITEM": 3,    # Bolsista
        "SITUACAO": "A"
    })

    if not bolsistas or len(bolsistas) < bolsas:
        if not SIEBolsistas().isBolsista(request.vars.ID_CURSO_ALUNO):
            for aluno in session.alunosPossiveis:
                if aluno['ID_CURSO_ALUNO'] == int(request.vars.ID_CURSO_ALUNO):
                    projeto = SIEProjetos().getProjetoDados(request.vars.ID_PROJETO)
                    SIEParticipantesProjs().criarParticipanteBolsista(projeto, aluno, session.edicao)
                    try:
                        MailBolsista(aluno, projeto).sendConfirmationEmail()
                    except Exception:
                        pass
                    return dict(success=True)
            return dict(success=False, msg="Aluno não está apto a receber uma bolsa.")
        return dict(success=False, msg="Aluno já recebe outra bolsa.")
    return dict(success=False, msg="Todas as bolsas já foram utilizadas. Remova algum participante e tente novamente.")



@auth.requires(proj.isCoordenador() and proj.registroBolsistaAberto(request.vars.ID_PROJETO))
def ajaxRemoverParticipante():
    participante = SIEParticipantesProjs().getParticipante(request.vars.ID_PARTICIPANTE)
    try:
        SIEParticipantesProjs().inativarParticipante(participante)
        response.flash = "Aluno removido com sucesso."
    except Exception:
        return "Não foi possível remover participante"


def ajaxCarregarAgencias():
    agencia = lambda ag: str(OPTION("%s-%s  %s" % (ag['COD_AGENCIA'], ag['DV_AGENCIA'], ag['NOME_AGENCIA']), _value=a['ID_AGENCIA']))
    for a in SIEAgencias().getAgenciasDeBanco(request.vars.ID_BANCO):
        yield agencia(a)
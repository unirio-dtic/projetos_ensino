# -*- coding: utf-8 -*-
from SIEFuncionarios import SIEFuncionarioID


def requires_edicao(f):
    if not session.edicao:
        session.flash = 'Você precisa selecionar uma edição'
        redirect(URL('registro', 'index'))
    return f


def index():
    from forms import FormEdicoes
    session.edicao = None

    form = FormEdicoes().form()

    if form.process().accepted:
        session.edicao = db(db.edicao.id == form.vars.edicao).select().first()

        session.funcionario = SIEFuncionarioID("12330675755").getFuncionarioIDs()
        redirect(URL('registro', 'registro'))

    return dict(form=form)


def registro():
    from SIEProjetos import SIEProjetos, SIEClassificacoesPrj
    from forms import FormProjetos

    classificacoes = SIEClassificacoesPrj().getClassificacoesPrj()

    form = FormProjetos(classificacoes).formRegistro()
    if form.process().accepted:
        projetos = SIEProjetos()
        projetos.salvarProjeto(form.vars)

    else:
        pass

    return dict(form=form)



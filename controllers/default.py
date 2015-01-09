# -*- coding: utf-8 -*-
from sie.SIEFuncionarios import SIEFuncionarioID


def index():
    redirect(URL("registro", "registro"))


@auth.requires_login()
def edicoes():
    from forms import FormEdicoes

    session.edicao = None

    form = FormEdicoes().form()

    if form.process().accepted:
        session.edicao = db(db.edicao.id == form.vars.edicao).select().first()
        try:
            session.funcionario = SIEFuncionarioID(session.auth.user.username).getFuncionarioIDs()
        except ValueError:
            session.flash = "Seus dados não foram encontrados. É possível que você não esteja " \
                            "autorizado a acessar este recurso."
            redirect(URL("default", "index"))

        redirect(URL('registro', 'registro'))

    return dict(form=form)


def user():
    return dict(form=auth())

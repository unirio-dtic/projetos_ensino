# -*- coding: utf-8 -*-
from datetime import date


def index():
    editalAberto = db((db.edicao.dt_inicial <= date.today()) & (db.edicao.dt_conclusao >= date.today())
    ).select(cache=(cache.ram, 86400), cacheable=True).first()

    if editalAberto:
        return dict(
            edital=editalAberto,
            dataFinal=editalAberto.dt_conclusao.strftime('%d/%m/%Y')
        )
    else:
        return dict()

@auth.requires_login()
def edicoes():
    from forms import FormEdicoes

    try:
        form = FormEdicoes().form()

        if form.process().accepted:
            session.edicao = db(db.edicao.id == form.vars.edicao).select().first()
            if request.vars._next:
                redirect(request.vars._next)

        return dict(form=form)
    except TypeError:
        return dict(form=None)


def user():
    response.view = 'default/login.html'
    return dict(form=auth())


def login():
    return dict(form=auth.login())
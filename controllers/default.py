# -*- coding: utf-8 -*-


def index():
    redirect(URL("registro", "registro"))


@auth.requires_login()
def edicoes():
    from forms import FormEdicoes

    session.edicao = None
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
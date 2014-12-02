# coding=utf-8
from gluon.tools import Crud


def cadastro_edicoes():
    edicoes = Crud(db).select(db.edicao)
    form = SQLFORM(db.edicao)

    if form.process().accepted:
       response.flash = 'form accepted'


    return dict(
        edicoes=edicoes if edicoes else "Nenhuma edição cadastrada",
        form=form
    )
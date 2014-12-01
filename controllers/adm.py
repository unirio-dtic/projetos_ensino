
def cadastro_edicoes():
    form = SQLFORM(db.edicao)
    return dict(form=form)
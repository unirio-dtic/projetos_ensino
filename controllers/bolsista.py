# coding=utf-8


@auth.requires(pessoa.isAluno())
def dados():
    session.flash = 'Indisponível no momento.'
    redirect(URL('default', 'index'))
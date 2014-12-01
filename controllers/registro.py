# -*- coding: utf-8 -*-

#@auth.requires_login()
def index():
    from SIEProjetos import SIEProjetos, SIEClassificacoesPrj
    from forms import FormProjetos

    classificacoes = SIEClassificacoesPrj().getClassificacoesPrj()

    form = FormProjetos(classificacoes).formRegistro()
    # form = FormProjetos(classificacoes).registroFactory()
    if form.process().accepted:
        try:
            projetos = SIEProjetos()
            projetos.salvarProjeto(form.vars)
        except Exception as e:
            response.flash = e.message

    else:
        pass

    return dict(form=form)



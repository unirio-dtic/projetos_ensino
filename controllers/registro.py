# -*- coding: utf-8 -*-

#@auth.requires_login()
def index():
    from SIEProjetos import SIEProjetos, SIEClassificacoesPrj

    classificacoes = SIEClassificacoesPrj().getClassificacoesPrj()

    form = FORM(
        SELECT([OPTION(classificacao['DESCRICAO'], _value=classificacao['ID_CLASSIFICACAO']) for classificacao in classificacoes], _name='ID_CLASSIFICACAO'),

        INPUT(_type='text', _name='TITULO'),
        TEXTAREA(_name='RESUMO'),
        INPUT(_type='text', _name='OBSERVACAO'),
        INPUT(_type='text', _name='PALAVRA_CHAVE01'),
        INPUT(_type='text', _name='PALAVRA_CHAVE02'),
        INPUT(_type='text', _name='PALAVRA_CHAVE03'),
        INPUT(_type='text', _name='PALAVRA_CHAVE04'),
        INPUT(_type='submit', _value='Salvar')
    )

    if form.process().accepted:
        try:
            projetos = SIEProjetos()
            projetos.salvarProjeto(form.vars)
        except Exception as e:
            response.flash = e.message

    else:
        pass

    return dict(form=form)



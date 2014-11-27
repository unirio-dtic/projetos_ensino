# -*- coding: utf-8 -*-
from gluon.html import *


class FormProjetos(object):
    def __init__(self, classificacoes):
        self.classificacoes = classificacoes

    def formRegistro(self):
        return FORM(
            LABEL('Classificação principal*:', _for='ID_CLASSIFICACAO'),
            SELECT([OPTION(classificacao['DESCRICAO'], _value=classificacao['ID_CLASSIFICACAO']) for classificacao in
                    self.classificacoes], _name='ID_CLASSIFICACAO'),

            BR(),
            INPUT(_type='text', _name='TITULO'),
            BR(),
            TEXTAREA(_name='RESUMO'),
            BR(),
            INPUT(_type='text', _name='OBSERVACAO'),
            BR(),
            INPUT(_type='text', _name='PALAVRA_CHAVE01'),
            BR(),
            INPUT(_type='text', _name='PALAVRA_CHAVE02'),
            BR(),
            INPUT(_type='text', _name='PALAVRA_CHAVE03'),
            BR(),
            INPUT(_type='text', _name='PALAVRA_CHAVE04'),
            BR(),
            INPUT(_type='submit', _value='Salvar')
        )
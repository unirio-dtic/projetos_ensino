# -*- coding: utf-8 -*-
from gluon import SQLFORM, Field, IS_NOT_EMPTY
from gluon.html import *


class FormProjetos(object):
    def __init__(self, classificacoes):
        self.classificacoes = classificacoes

    def formRegistro(self):
        return FORM(
            self._selectComponent(
                'Classificação principal*:',
                'ID_CLASSIFICACAO',
                [OPTION(classificacao['DESCRICAO'], _value=classificacao['ID_CLASSIFICACAO']) for classificacao in
                 self.classificacoes]
            ),
            self._inputComponent("Título*:", "TITULO"),
            self._bigTextComponent("Resumo*:", "RESUMO"),
            self._inputComponent("Observação*:", "OBSERVACAO"),
            self._inputComponent("Palavra-chave*:", "PALAVRA_CHAVE01"),
            self._inputComponent("Palavra-chave*:", "PALAVRA_CHAVE02"),
            self._inputComponent("Palavra-chave*:", "PALAVRA_CHAVE03"),
            self._inputComponent("Palavra-chave*:", "PALAVRA_CHAVE04"),
            INPUT(_type='submit', _value='Salvar')
        )

    def _inputComponent(self, label, name, isNotEmpty=True):
        return self._component(INPUT(_name=name, _id=name, requires=IS_NOT_EMPTY() if isNotEmpty else None),
                               label,
                               name)

    def _bigTextComponent(self, label, name, isNotEmpty=True):
        return self._component(TEXTAREA(_name=name, _id=name, requires=IS_NOT_EMPTY() if isNotEmpty else None),
                               label,
                               name)

    def _selectComponent(self, label, name, options, isNotEmpty=True):
        return self._component(SELECT(*options, _name=name, _id=name, requires=IS_NOT_EMPTY()), label, name)

    def _component(self, component, label, name):
        return SPAN(
            LABEL(label + " ", _for=name),
            component,
            BR()
        )

    def registroFactory(self):
        return SQLFORM.factory(
            Field("TITULO", label="Título*", requires=IS_NOT_EMPTY()),
            Field("RESUMO", "text", label="Resumo*"),
            Field("OBSERVACAO", label="Observação"),
            Field("PALAVRA_CHAVE01", label="Palavra-chave"),
            Field("PALAVRA_CHAVE02", label="Palavra-chave"),
            Field("PALAVRA_CHAVE03", label="Palavra-chave"),
            Field("PALAVRA_CHAVE04", label="Palavra-chave"),
        )

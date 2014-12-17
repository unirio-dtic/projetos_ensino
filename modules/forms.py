# -*- coding: utf-8 -*-
from datetime import date
from gluon import SQLFORM, Field, IS_NOT_EMPTY, current
from gluon.html import *


class CustomFormHelper(object):
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


class FormEdicoes(CustomFormHelper):
    def __init__(self):
        self.db = current.db

    @property
    def edicoes(self):
        """
        Retorna um SELECT com as edições possiveis de cadastro para a data atual

        :rtype : gluon.html.SELECT
        :return: Um SELECT com as possíeis edições
        """
        edicoes = self.db((self.db.edicao.dt_inicial <= date.today())
                          &(self.db.edicao.dt_conclusao >= date.today())).select()
        if edicoes:
            return [OPTION(edicao.nome, _value=edicao.id) for edicao in edicoes]

    def form(self):
        return FORM(
            self._selectComponent("Edição*:", "edicao", self.edicoes),
            INPUT(_type='submit', _value='Selecionar Edição')
        )


class FormProjetos(CustomFormHelper):
    def __init__(self, classificacoes, cursos):
        self.classificacoes = classificacoes
        self.cursos = cursos

    def formRegistro(self):
        return FORM(
            self._selectComponent(
                'Classificação principal*:',
                'ID_CLASSIFICACAO',
                [OPTION(classificacao['DESCRICAO'], _value=classificacao['ID_CLASSIFICACAO']) for classificacao in
                 self.classificacoes]
            ),
            self._selectComponent(
                'Curso*:',
                'ID_CURSO',
                [OPTION(curso['NOME_CURSO'], _value=curso['ID_CURSO']) for curso in
                 self.cursos]
            ),
            self._inputComponent("Título*:", "TITULO"),
            self._bigTextComponent("Resumo*:", "RESUMO"),
            self._inputComponent("Observação:", "OBSERVACAO"),
            self._inputComponent("Palavra-chave 1*:", "PALAVRA_CHAVE01"),
            self._inputComponent("Palavra-chave 2*:", "PALAVRA_CHAVE02"),
            self._inputComponent("Palavra-chave 3:", "PALAVRA_CHAVE03"),
            self._inputComponent("Palavra-chave 4:", "PALAVRA_CHAVE04"),
            INPUT(_type='submit', _value='Salvar')
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

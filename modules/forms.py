# -*- coding: utf-8 -*-
from datetime import date

from gluon import SQLFORM, Field, IS_NOT_EMPTY, current
from gluon.html import *


class CustomFormHelper(object):
    def _inputComponent(self, label, name, isNotEmpty=True):
        return self._component(INPUT(_name=name, _id=name, requires=IS_NOT_EMPTY() if isNotEmpty else None),
                               label,
                               name)

    def _checkboxComponenet(self, label, name, isNotEmpty=True):
        return self._invertedCompent(INPUT(_name=name, _id=name, requires=IS_NOT_EMPTY() if isNotEmpty else None, _type="checkbox"),
                               label,
                               name)

    def _fileComponent(self, label, name, isNotEmpty=True):
        return self._component(
            INPUT(_type="file", _name=name, _id=name, requires=IS_NOT_EMPTY() if isNotEmpty else None),
            label,
            name)

    def _bigTextComponent(self, label, name, isNotEmpty=True):
        return self._component(TEXTAREA(_name=name, _id=name, requires=IS_NOT_EMPTY() if isNotEmpty else None),
                               label,
                               name)

    def _selectComponent(self, label, name, options, isNotEmpty=True):
        return self._component(SELECT(*options, _name=name, _id=name, requires=IS_NOT_EMPTY() if isNotEmpty else None), label, name)


    def _invertedCompent(self, component, label, name):
        return SPAN(
            component,
            LABEL(" " + label, _for=name),
            BR()
        )

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

        :rtype : list
        :return: Um SELECT com as possíveis edições
        """
        edicoes = self.db((self.db.edicao.dt_inicial <= date.today())
                          & (self.db.edicao.dt_conclusao >= date.today())).select(cache=(current.cache.ram, 86400),
                                                                                  cacheable=True)
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
        self.cursos = list(cursos)
        self.cursos.insert(0, {'ID_CURSO': '', 'NOME_CURSO': 'Selecione'})

    def formRegistro(self):
        return FORM(
            FIELDSET(
                self._selectComponent(
                    'Classificação principal*:',
                    'ID_CLASSIFICACAO',
                    [OPTION(classificacao['DESCRICAO'], _value=classificacao['ID_CLASSIFICACAO']) for classificacao in
                     self.classificacoes]
                ),
                INPUT(_type='hidden', _id='ID_UNIDADE', _name='ID_UNIDADE'),
                self._selectComponent(
                    'Curso*:',
                    'ID_CURSO',
                    [OPTION(curso['NOME_CURSO'], _value=curso['ID_CURSO']) for curso in
                     self.cursos]
                ),
                self._selectComponent(
                    'Disciplina*:',
                    'COD_DISCIPLINA',
                    [OPTION('Selecione o curso', _value='')]
                ),
                self._inputComponent("Título*:", "TITULO"),
                self._bigTextComponent("Resumo*:", "RESUMO"),
                self._inputComponent("Observação:", "OBSERVACAO", False),
                self._inputComponent("Palavra-chave 1*:", "PALAVRA_CHAVE01"),
                self._inputComponent("Palavra-chave 2*:", "PALAVRA_CHAVE02"),
                self._inputComponent("Palavra-chave 3:", "PALAVRA_CHAVE03", False),
                self._inputComponent("Palavra-chave 4:", "PALAVRA_CHAVE04", False)
            ),
            FIELDSET(
                self._selectComponent('Quantidade de bolsas*:', 'quantidade_bolsas', range(1, 3))
            ),
            FIELDSET(
                self._fileComponent("Projeto*:", "CONTEUDO_ARQUIVO1"),
                self._fileComponent("Ata do Departamento*:", "CONTEUDO_ARQUIVO5"),
                self._fileComponent("Relatório Docente:", "CONTEUDO_ARQUIVO14", False),
                self._fileComponent("Relatório de Bolsista:", "CONTEUDO_ARQUIVO17", False)
            ),
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


class FormPerguntas(CustomFormHelper):
    def __init__(self, perguntas):
        """


        :type perguntas: list
        :param perguntas:
        """
        self.perguntas = perguntas

    def formAvaliacao(self):
        perguntas = [self._checkboxComponenet(p.pergunta, p.id, False) for p in self.perguntas]
        perguntas.append(self._bigTextComponent("Observações:", "observacao", False))
        perguntas.append(INPUT(_type="submit", _value="Salvar"))

        return FORM(perguntas)

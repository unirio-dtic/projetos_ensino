# -*- coding: utf-8 -*-
from sie.SIEBancos import SIEBancos
from gluon import IS_NOT_EMPTY, current, IS_UPLOAD_FILENAME
from gluon.html import *


class CustomFormHelper(object):
    def _inputComponent(self, label, name, isNotEmpty=True, **kwargs):
        return self._component(INPUT(_name=name, _id=name, requires=IS_NOT_EMPTY() if isNotEmpty else None, **kwargs),
                               label,
                               name)

    def _checkboxComponenet(self, label, name, isNotEmpty=True):
        return self._invertedCompent(
            INPUT(_name=name, _id=name, requires=IS_NOT_EMPTY() if isNotEmpty else None, _type="checkbox"),
            label,
            name)

    def _fileComponent(self, label, name, isNotEmpty=True):
        return self._component(
            INPUT(_type="file", _name=name, _id=name, requires=IS_UPLOAD_FILENAME(extension='pdf',
                                                                                  error_message="O arquivo precisa ser um PDF.") if isNotEmpty else None),
            label,
            name)

    def _bigTextComponent(self, label, name, isNotEmpty=True, **kwargs):
        return self._component(
            TEXTAREA(_name=name, _id=name, requires=IS_NOT_EMPTY() if isNotEmpty else None, **kwargs),
            label,
            name)

    def _selectComponent(self, label, name, options, isNotEmpty=True, **kwargs):
        return self._component(SELECT(*options, _name=name, _id=name, requires=IS_NOT_EMPTY() if isNotEmpty else None,
                                      **kwargs),
                               label, name)


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
        edicoes = self.db(self.db.edicao).select(cache=(current.cache.ram, 86400), cacheable=True)
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
                    [OPTION(curso['NOME_CURSO'], _value=curso['ID_CURSO']) for curso in self.cursos],
                    _onchange='ajax("%s", ["ID_CURSO"], "COD_DISCIPLINA")' % URL('registro', 'ajaxDisciplinas')
                ),
                self._selectComponent(
                    'Disciplina*:',
                    'COD_DISCIPLINA',
                    [OPTION('Selecione o curso', _value='')]
                ),
                self._inputComponent("Título*:", "TITULO"),
                self._bigTextComponent("Resumo*:", "RESUMO", _maxlength=10000),
                self._inputComponent("Observação:", "OBSERVACAO", False),
                self._inputComponent("Palavra-chave 1*:", "PALAVRA_CHAVE01", _maxlength=20),
                self._inputComponent("Palavra-chave 2*:", "PALAVRA_CHAVE02", _maxlength=20),
                self._inputComponent("Palavra-chave 3:", "PALAVRA_CHAVE03", False, _maxlength=20),
                self._inputComponent("Palavra-chave 4:", "PALAVRA_CHAVE04", False, _maxlength=20)
            ),
            FIELDSET(
                self._selectComponent('Quantidade de bolsas*:', 'quantidade_bolsas', range(1, 3))
            ),
            INPUT(_type='submit', _value='Salvar e Prosseguir')
        )


class FormArquivos(CustomFormHelper):
    def formArquivoProjeto(self):
        return FORM(
            self._fileComponent("Projeto*:", "CONTEUDO_ARQUIVO"),
            INPUT(_type='submit', _value='Salvar e Prosseguir')
        )

    def formArquivoAta(self):
        return FORM(
            self._fileComponent("Ata do Departamento*:", "CONTEUDO_ARQUIVO"),
            INPUT(_type='submit', _value='Salvar e Prosseguir')
        )

    def formArquivoRelatioDocente(self):
        return FORM(
            self._fileComponent("Relatório Docente:", "CONTEUDO_ARQUIVO", False),
            INPUT(_type='submit', _value='Salvar e Prosseguir')
        )

    def formArquivoRelatorioBolsista(self):
        return FORM(
            self._fileComponent("Relatório de Bolsista:", "CONTEUDO_ARQUIVO", False),
            INPUT(_type='submit', _value='Salvar e Prosseguir')
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
        perguntas.append(INPUT(_type="submit", _value="Indeferir"))

        return FORM(perguntas)


class FormBolsista(CustomFormHelper):
    def formCadastroBolsista(self):
        bancos_options = [OPTION(banco['NOME_BANCO'], _value=banco['ID_BANCO']) for banco in SIEBancos().getBancos()]

        return FORM(
            FIELDSET(
                LEGEND("Dados Bancários"),
                self._selectComponent("Banco*", "ID_BANCO", bancos_options, _onchange='ajax("%s", ["ID_BANCO"], "ID_AGENCIA")' % URL('bolsista', 'ajaxCarregarAgencias')),
                self._selectComponent(
                    'Agência*:',
                    'ID_AGENCIA',
                    [OPTION('Selecione o banco', _value='')]
                ),
                self._inputComponent("Conta Corrente*", "CONTA_CORRENTE"),
                INPUT(_value='Enviar', _type='submit')
            )
        )


class FormAlteracaoDisciplina(CustomFormHelper):
    def __init__(self, cursos):
        self.cursos = list(cursos)
        self.cursos.insert(0, {'ID_CURSO': '', 'NOME_CURSO': 'Selecione'})

    def form(self):
        return FORM(
            self._selectComponent(
                'Curso*:',
                'ID_CURSO',
                [OPTION(curso['NOME_CURSO'], _value=curso['ID_CURSO']) for curso in self.cursos],
                _onchange='ajax("%s", ["ID_CURSO"], "COD_DISCIPLINA")' % URL('registro', 'ajaxDisciplinas')
            ),
            self._selectComponent(
                'Disciplina*:',
                'COD_DISCIPLINA',
                [OPTION('Selecione o curso', _value='')]
            ),
            INPUT(_value='Salvar Alterações', _type='submit')
        )


class FormMeses(CustomFormHelper):
    def __init__(self):
        self.db = current.db

    @property
    def anos(self):
        #TODO Esse hack não deveria ser necessário. A consulta de dates não está retornando dt_presenca como chave
        dates = self.db().select(self.db.edicao.dt_inicial_projeto.year(), distinct=True)
        return [int(ano[0]) for ano in dates.response]

    @property
    def meses(self):
        return range(1, 13)

    def form(self):
        return FORM(
            self._selectComponent('Ano :', 'ano', self.anos),
            self._selectComponent('Mês :', 'mes', self.meses),
            self._checkboxComponenet('Filtrar ativos ?', 'ativos', False),
            INPUT(_value='Buscar', _type='submit')
        )
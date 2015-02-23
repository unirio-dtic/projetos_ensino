# coding=utf-8
from datetime import date
from sie.SIEAlunos import SIEAlunos
from sie.SIEProjetos import SIEProjetos
from sie.SIEFuncionarios import SIEFuncionarioID
from gluon import current, redirect, URL

__author__ = 'diogomartins'


class Edicao(object):
    def __init__(self, db):
        self.db = db

    def requires_edicao(self):
        """
        Usado para verificar se o usuário selecionou uma edição
        """
        if current.session.edicao:
            return True
        else:
            redirect(
                URL('default', 'edicoes', vars=dict(_next=URL(current.request.controller, current.request.function))))

    def isValidEdicaoForRegistro(self, edicao):
        if self.db((self.db.edicao.dt_inicial <= date.today()) & (self.db.edicao.dt_conclusao >= date.today()) & (
                    self.db.edicao.id == edicao.id)).select(cache=(current.cache.ram, 86400), cacheable=True):
            return True


class Projeto(object):
    def __init__(self, db):
        self.db = db

    def requires_projeto(self):
        if current.session.projeto:
            return True

    def registroBolsistaAberto(self, ID_PROJETO):
        if self.db((self.db.edicao.dt_inicial_bolsistas <= date.today()) & (
                    self.db.projetos.edicao == self.db.edicao.id) & (
                    self.db.projetos.id_projeto == ID_PROJETO)).select().first():
            return True

    def isCoordenador(self):
        coordenador = SIEProjetos().getCoordenador(current.request.vars.ID_PROJETO)
        if coordenador['ID_PESSOA'] == current.session.funcionario['ID_PESSOA']:
            return True


class Pessoa(object):
    def __init__(self, db):
        self.db = db

    def isFuncionario(self):
        try:
            if not current.session.funcionario:
                current.session.funcionario = SIEFuncionarioID(current.session.auth.user.username).getFuncionarioIDs()
            return True
        except (ValueError, AttributeError):
            return False

    def isAluno(self):
        try:
            if not current.session.aluno:
                current.session.aluno = SIEAlunos().getAlunoAtivoFromCPF(current.session.auth.user.username)
            return True
        except (ValueError, AttributeError):
            return False
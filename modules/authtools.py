# coding=utf-8
from datetime import date
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
            redirect(URL('default', 'edicoes', vars=dict(_next=URL(current.request.controller, current.request.function))))

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


class Pessoa(object):
    def __init__(self, db):
        self.db = db

    def isFuncionario(self):
        try:
            if not current.session.funcionario:
                current.session.funcionario = SIEFuncionarioID(current.session.auth.user.username).getFuncionarioIDs()
            return True
        except ValueError:
            current.session.flash = "Seus dados não foram encontrados. É possível que você não esteja autorizado a acessar este recurso."

    def isAluno(self):
        return True
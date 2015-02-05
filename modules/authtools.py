# coding=utf-8
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
            current.session.flash = "Você precisa selecionar uma edição."
            redirect(
                URL("default", "edicoes", vars={"_next": URL(current.request.controller, current.request.function)}))


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
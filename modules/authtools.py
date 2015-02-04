# coding=utf-8
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
            redirect(URL("default", "edicoes", vars={"_next": URL(current.request.controller, current.request.function)}))


class Projeto(object):
    def __init__(self, db):
        self.db = db

    def requires_projeto(self):
        if current.session.projeto:
            return True
        else:
            redirect(URL("consulta", "index"))
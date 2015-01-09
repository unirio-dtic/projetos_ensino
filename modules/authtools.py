# coding=utf-8
from gluon import current, redirect, URL

__author__ = 'diogomartins'


class Edicao(object):
    def __init__(self, db):
        self.db = db

    def requires_edicao(self):
        """
        Decorator para verifiicar se o usuário selecionou uma edição
        :param f:
        :type f: callable
        """
        def wrapper():
            if not current.session.edicao:
                redirect(URL("default", "edicoes"))
            else:
                pass
        return wrapper()
# coding=utf-8
from datetime import datetime

from gluon import current


class Avaliacao(object):
    def __init__(self):
        self.db = current.db
        self.api = current.api
        self.cacheTime = 86400

    def getAvaliador(self, ID_PROJETO):
        user = self.db((self.db.avaliacao.id_projeto == ID_PROJETO) & (
            self.db.avaliacao.avaliador == self.db.auth_user.id)).select(self.db.auth_user.username,
                                                                         cache=(current.cache.ram, self.cacheTime)
        ).first()

        if user:
            try:
                avaliador = self.api.performGETRequest("V_FUNCIONARIO_IDS", {"CPF": user.username, "LMIN": 0, "LMAX": 1}, cached=self.cacheTime)
                return avaliador.content[0]["NOME_PESSOA"]
            except AttributeError:
                return "Funcionário não encontrado"
        return "Indisponível"

    def salvarAvaliacao(self, ID_PROJETO):
        return self.db.avaliacao.insert(
            avaliador=current.session.auth.user.id,
            id_projeto=ID_PROJETO,
            datahora=datetime.now()
        )

    def isAvaliado(self, ID_PROJETO):
        if self.db(self.db.avaliacao.id_projeto == ID_PROJETO).select().first():
            return True

    def indeferir(self):
        pass


#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
from unittest import TestCase

web2py_path = '../../..'
sys.path.append(os.path.realpath(web2py_path))
os.chdir(web2py_path)

from gluon.globals import Request, Session
from gluon.shell import exec_environment
from gluon.storage import Storage
from datetime import datetime
from cgi import FieldStorage


class TestRegistroController(TestCase):
    def setUp(self):
        self.env, self.db = setup('init', 'default', db_name='db', db_link='sqlite:memory:')
        self.request = Request()
        self.session = Session()
        self.controller = exec_environment('applications/projs/controllers/registro.py', request=self.request)
        self.controller.response.view = 'unittest.html'
        self.session.funcionario = {
            "CPF": "1330675755",
            "ID_FUNCIONARIO": 11414,
            "ID_PESSOA": 33694,
            "ID_USUARIO": 21771
        }

    def testeRegistroWithValid(self):
        self.request.env.request_method = 'POST'
        self.request.vars = Storage(
            COD_DISCIPLINA='11ANG002',
            CONTEUDO_ARQUIVO1=FieldStorage(fp=open("static/arquivoteste.pdf", 'rb')),
            CONTEUDO_ARQUIVO5=FieldStorage(fp=open("static/arquivoteste.pdf", 'rb')),
            CONTEUDO_ARQUIVO14=FieldStorage(fp=open("static/arquivoteste.pdf", 'rb')),
            CONTEUDO_ARQUIVO17=FieldStorage(fp=open("static/arquivoteste.pdf", 'rb')),
            ID_CLASSIFICACAO=40161,
            ID_CURSO=320,
            ID_UNIDADE=868,
            OBSERVACAO='observacao teste',
            PALAVRA_CHAVE01='palavra1',
            PALAVRA_CHAVE02='palavra2',
            PALAVRA_CHAVE03='palavra3',
            PALAVRA_CHAVE04='palavra4',
            RESUMO='Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, '
                   'totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta '
                   'sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia'
                   ' consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt. Neque porro quisquam est, '
                   'qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi'
                   ' tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem. Ut enim ad minima veniam,'
                   ' quis nostrum exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid ex ea commodi'
                   ' consequatur? Quis autem vel eum iure reprehenderit qui in ea voluptate velit esse quam nihil'
                   ' molestiae consequatur, vel illum qui dolorem eum fugiat quo voluptas nulla pariatur?',
            TITULO='Meu trabalho de teste %s' % str(datetime.now()),
            quantidade_bolsas=1
        )
        self.controller.registro()
        form = self.controller.response._vars['form']
        self.assertFalse(form.erros)


if __name__ == '__main__':
    unittest.main()

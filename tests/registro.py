#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
web2py_path = '../../..'
sys.path.append(os.path.realpath(web2py_path))
os.chdir(web2py_path)

import unittest
from gluon.globals import Request, Session
from gluon.shell import exec_environment
from gluon.storage import Storage


class TestRegistroController(unittest.TestCase):
    def setUp(self):
        self.request = Request()
        self.session = Session()
        self.controller = exec_environment('applications/projs/controllers/registro.py', request=self.request)
        self.controller.response.view = 'unittest.html'

    def testeRegistroWithValid(self):
        self.request.env.request_method = 'POST'
        self.request.vars = Storage(

        )
        self.controller.contact()
        form = self.controller.response._vars['form']
        self.assertTrue(form.errors)
        self.assertTrue(form.errors.has_key('email'))
        self.assertEqual(form.errors['email'], 'invalid email!')


if __name__ == '__main__':
    unittest.main()

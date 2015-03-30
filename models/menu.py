# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.logo = A("DTIC/UNIRIO",
                  _class="brand",_href="http://www.unirio.br/dtic")
response.title = request.application.replace('_', ' ').title()
response.subtitle = ''

## read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Diogo Magalhães Martins <diogo.martins@unirio.br>'
response.meta.keywords = 'UNIRIO, Projetos de Ensino, Bolsa, Monitoria'
response.meta.generator = 'Web2py Web Framework'

## your http://google.com/analytics id
response.google_analytics_id = None

#########################################################################
## this is the main application menu add/remove items as required
#########################################################################

response.menu = [
    ('Transparência', False, False, [
        ('Bolsistas Ativos', False, URL('transparencia', 'bolsistas'), []),
        ('Bolsas por unidade', False, URL('transparencia', 'bolsas_unidades'), []),
        ('Projetos Aprovados', False, URL('transparencia', 'projetos_aprovados'), [])
    ])
]

if auth.is_logged_in():
    response.menu[:] += [
        ('Edições', False, URL('default', 'edicoes'), []),
        ('Registro', False, False, [
            ("Registro de Projeto", False, URL('registro', 'registro')),
            ("Registro de Bolsista", False, URL('consulta', 'aprovados'))
        ]),
        ("Acompanhamento", False, URL('consulta', 'index'))
    ]

admin_menu = [
    ('Administração', False, False, [
        ('Edições', False, False, [
            ('Cadastro de Edições', False, URL("adm", "cadastro_edicoes"), []),
            ('Cadastro de Perguntas', False, URL("adm", "cadastro_perguntas"), [])
        ]),
        ('Avaliação de Projetos', False, URL("adm", "avaliacao"), []),
        ('Relatórios', False, False, [
            ('Lista de Deferidos', False, URL("adm", "deferidos"), []),
            ('Lista de Indeferidos', False, URL("adm", "indeferidos"), []),
            ('Bolsistas Ativos', False, URL('adm', 'bolsistas_ativos'), [])
        ]),
        ('Avaliadores', False, URL('adm', 'avaliadores'), [])
    ])
]

if auth.has_membership('DTIC') or auth.has_membership('PROGRAD'):
    response.menu += admin_menu

if "auth" in locals(): auth.wikimenu() 

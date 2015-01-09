# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.logo = A("DTIC/UNIRIO",
                  _class="brand",_href="http://www.unirio.br/dtic")
response.title = request.application.replace('_',' ').title()
response.subtitle = ''

## read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Your Name <you@example.com>'
response.meta.keywords = 'web2py, python, framework'
response.meta.generator = 'Web2py Web Framework'

## your http://google.com/analytics id
response.google_analytics_id = None

#########################################################################
## this is the main application menu add/remove items as required
#########################################################################

response.menu = [
    (T('Edições'), False, URL('default', 'edicoes'), [])
]


response.menu += [
    (T('Registro'), False, False, [
        ("Registro", False, URL('registro', 'registro')),
        ("Acompanhamento", False, URL('consulta', 'index'))
    ])
]
admin_menu = [
    (T('Administração'), False, False, [
        (T('Cadastro de Edições'), False, URL("adm", "cadastro_edicoes"), []),
        (T('Avaliação de Projetos'), False, URL("adm", "avaliacao"), [])
    ])

]

if auth.has_membership('DTIC') or auth.has_membership('PROGRAD'):
    response.menu += admin_menu

if "auth" in locals(): auth.wikimenu() 

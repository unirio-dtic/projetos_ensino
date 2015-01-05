# -*- coding: utf-8 -*-


from gluon.tools import Auth, Service, PluginManager

auth = Auth(db)
service = Service()
plugins = PluginManager()

## create all tables needed by auth if not custom tables
auth.define_tables(username=True, signature=False)
auth.settings.actions_disabled = [
    'register',
    'retrieve_username',
    'profile',
    'lost_password'
]
db.auth_user.username.label = 'CPF'

if not request.is_local:
    from gluon.contrib.login_methods.ldap_auth import ldap_auth
    auth.settings.login_methods=[ldap_auth(mode='uid', server='ldap.unirio.br', base_dn='ou=people,dc=unirio,dc=br')]

db.define_table(
    'edicao',
    Field('nome', 'string', notnull=True, required=True, label='Edital*'),
    Field('dt_inicial', 'date', notnull=True, required=True, label='Data inicial de registro*'),
    Field('dt_conclusao', 'date', notnull=True, required=True, label="Data final de registro*"),
    Field('dt_inicial_projeto', 'date', notnull=True, required=True, label='Data inicial do projeto*'),
    Field('dt_conclusao_projeto', 'date', notnull=True, required=True, label="Data final do projeto*"),
    Field('disciplinas_obrigatorias', 'boolean', notnull=True, required=True, label='Mostrar somente disciplinas obrigatórias?*'))

db.define_table(
    'projetos',
    Field('anexo', 'blob'),
    Field('anexo_nome', 'string'),
    Field('anexo_tipo', 'string'),
    Field('id_projeto', 'integer'),
    Field('id_funcionario', 'integer')
)

## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' if request.is_local else 'smtp.gmail.com:587'
mail.settings.sender = 'you@gmail.com'
mail.settings.login = 'username:password'

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

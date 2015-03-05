# coding=utf-8
from authtools import Edicao, Projeto, Pessoa
from gluon.tools import Auth, Service

auth = Auth(db)
service = Service()
edicao = Edicao(db)
proj = Projeto(db)
pessoa = Pessoa(db)

current.proj = proj

## create all tables needed by auth if not custom tables
auth.define_tables(username=True, signature=False)
auth.settings.actions_disabled = [
    'register',
    'retrieve_username',
    'profile',
    'lost_password'
]

db.auth_user.username.label = 'CPF'

from gluon.contrib.login_methods.ldap_auth import ldap_auth
auth.settings.login_methods=[ldap_auth(mode='uid', server='ldap.unirio.br', base_dn='ou=people,dc=unirio,dc=br')]

db.define_table(
    'edicao',
    Field('nome', 'string', notnull=True, required=True, label='Edital*'),
    Field('dt_inicial', 'date', notnull=True, required=True, label='Data inicial de registro*'),
    Field('dt_conclusao', 'date', notnull=True, required=True, label="Data final de registro*"),
    Field('dt_inicial_projeto', 'date', notnull=True, required=True, label='Data inicial do projeto*'),
    Field('dt_conclusao_projeto', 'date', notnull=True, required=True, label="Data final do projeto*"),
    Field('dt_inicial_bolsistas', 'date', notnull=True, required=True, label="Data inicial de registro de bolsistas"),
    Field('dt_conclusao_bolsistas', 'date', required=True, label="Data final de registro de bolsistas"),
    Field('disciplinas_obrigatorias', 'boolean', notnull=True, required=True, label='Mostrar somente disciplinas obrigatórias?*')
)

db.define_table(
    'projetos',
    Field('anexo_nome', 'string', notnull=True),
    Field('anexo_tipo', 'string', notnull=True),
    Field('id_arquivo_proj', 'integer'),
    Field('id_funcionario', 'integer', notnull=True),
    Field('id_projeto', 'integer', notnull=True),
    Field('edicao', db.edicao, notnull=True),
    Field('arquivo', 'upload'),
    Field('tipo_arquivo_item', 'integer'),
    Field('dt_envio', 'datetime'),
    Field("unique_validator", unique=True, compute=lambda r: str(r.id_projeto) + str(r.tipo_arquivo_item))
)

db.define_table(
    'bolsas',
    Field('id_projeto', 'integer'),
    Field('quantidade_bolsas', 'integer')
)

db.define_table(
    'avaliacao_perguntas',
    Field("edicao", db.edicao),
    Field("pergunta", "string")
)

db.define_table(
    'avaliacao',
    Field('avaliador', db.auth_user),
    Field('id_projeto', 'integer'),
    Field('dt_envio', 'datetime'),
    Field('is_deferido', 'boolean'),
    Field('observacao', 'text')
)

db.define_table(
    'avaliacao_respostas',
    Field('pergunta', db.avaliacao_perguntas),
    Field('avaliacao', db.avaliacao),
    Field('resposta', 'boolean'),
)

db.define_table(
    'log_admin',
    Field('acao', notnull=True),
    Field('valores', label='Valores antes da alteração'),
    Field('tablename'),
    Field('colname', 'string'),
    Field('uid', 'integer'),
    Field('dt_alteracao', 'datetime', notnull=True),
    Field('user_id', db.auth_user, notnull=True)
)

db.avaliacao_perguntas.edicao.requires = IS_IN_DB(db, 'edicao.id', '%(nome)s', zero='Selecione')
db.avaliacao_perguntas.pergunta.requires = IS_NOT_EMPTY()

db.projetos.arquivo.represent = lambda value, row: A(row.anexo_nome, _href=URL('download', args=value))

## configure email
mail = auth.settings.mailer
mail.settings.server = 'smtp.gmail.com:587'
mail.settings.sender = 'naoresponder.projetos@unirio.br'
mail.settings.login = 'naoresponder.projetos@unirio.br:8mx-SvY-fQh-SV9'

current.mail = mail

## configure auth policy
auth.settings.login_next = URL('default', 'mensagem')
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True
auth.settings.create_user_groups = None
auth.settings.actions_disabled = [
    'register',
    'retrieve_username',
    'remember_me',
    'profile',
    'change_password',
    'request_reset_password'
]

current.auth = auth

piwik_host = '200.156.24.35'
piwik_idSite = 1
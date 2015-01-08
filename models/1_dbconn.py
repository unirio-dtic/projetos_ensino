from gluon import current

kAPIKey = '9287c7e89bc83bbce8f9a28e7d448fa7366ce23f163d2c385966464242e0b387e3a34d0e205cb775d769a44047995075'

db = DAL('postgres://postgres:devdtic2@sistemas.unirio.br/projs', pool_size=5)

current.kAPIKey = kAPIKey
current.db = db
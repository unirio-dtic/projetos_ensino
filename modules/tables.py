# coding=utf-8
from gluon import current
from sie.SIEProjetos import SIEParticipantesProjs, SIEProjetos
from sie.SIEServidores import SIEServidores
from gluon.html import *

__all__ = [
    "TableAcompanhamento",
    "TableAvaliacao",
    "TableDeferimento",
    "TabelaProjetos"
]


class TableHelper(object):
    def __init__(self):
        self.podeAlterarSituacao = current.auth.has_permission("alterarSituacao")
        self.podeAlterarDisciplina = current.auth.has_permission("alterarDisciplina")
        self.humanHeaders = {
            'BOLSAS': 'Qtd. Bolsas',
            'BOLSISTA': 'Bolsista',
            'COD_DISCIPLINA': 'Cód. Disciplina',
            'COORDENADOR': 'Coordenador',
            'DT_REGISTRO': 'Data de registro',
            'NOME_DISCIPLINA': 'Disciplina',
            'NOME_UNIDADE': 'Departamento',
            'NUM_PROCESSO': 'Num. Processo',
            'VL_BOLSA': 'Valor'
        }

    def disciplina(self, p):
        if not self.podeAlterarDisciplina:
            return p['NOME_DISCIPLINA']
        else:
            return A(p['NOME_DISCIPLINA'], _href=URL('adm', 'alterarDisciplina', vars=dict(ID_PROJETO=p['ID_PROJETO'])))

    def num_processo(self, NUM_PROCESSO):
        return A(NUM_PROCESSO, _href=URL('processos', 'default', 'index', scheme='http', host='sistemas.unirio.br',
                                         vars={'NUM_PROCESSO': NUM_PROCESSO}))

    def vl_bolsa(self, VL_BOLSA):
        return 'R$%s' % VL_BOLSA


class TableProjetos(TableHelper):
    def __init__(self, projetos):
        """

            :type projetos: list
            """
        super(TableProjetos, self).__init__()
        self.db = current.db
        self.edicao = current.session.edicao
        bolsas = self.db((self.db.bolsas.id_projeto == self.db.projetos.id_projeto) & (
            self.db.projetos.edicao == self.edicao.id)).select(self.db.bolsas.ALL,
                                                               cache=(current.cache.ram, 86400))
        self.projetos = projetos
        self.podeAlterarBolsas = not current.auth.has_permission(
            "alterarBolsas") or current.proj.registroBolsistaAberto(current.session.edicao)
        self.situacoes = SIEProjetos().situacoes()
        self.bolsas = {b.id_projeto: b.quantidade_bolsas for b in bolsas}

    def arquivos(self, projeto):
        arquivos = current.db(current.db.projetos.id_projeto == projeto["ID_PROJETO"]).select()
        return UL([A(arquivo["anexo_nome"], _href=URL(f='download', args=arquivo["arquivo"])) for arquivo in arquivos])

    def coordenador(self, p):
        try:
            return SIEProjetos().getCoordenador(p['ID_PROJETO'])['NOME_PESSOA']
        except (TypeError, AttributeError):
            return "Indefinido"

    def situacao(self, p):
        try:
            if self.podeAlterarSituacao:
                return SELECT([OPTION(s['DESCRICAO'], _value=s['ITEM_TABELA']) for s in self.situacoes],
                              value=p['SITUACAO_ITEM'], _onchange='alterarSituacao(%d, this.value)' % p['ID_PROJETO'])
            else:
                return p['SITUACAO']
        except AttributeError:
            return "Aguardando..."

    def avaliacao(self, p):
        return p['AVALIACAO'] if p['AVALIACAO'] else "Avaliação não cadastrada"

    def avaliador(self, projeto):
        user = current.db((current.db.avaliacao.avaliador == current.db.auth_user.id) & (
            current.db.avaliacao.id_projeto == projeto['ID_PROJETO'])).select(current.db.auth_user.username,
                                                                              cache=(current.cache.ram, 86400)).first()
        try:
            servidor = SIEServidores().getServidorByCPF(user.username)
            return "Avaliado por %s" % servidor['NOME_FUNCIONARIO']
        except (TypeError, ValueError, AttributeError):
            return "Servidor não encontrado"

    def bolsa(self, p):
        try:
            if self.podeAlterarBolsas:
                return SELECT(
                    range(1, 3),
                    _name=p['ID_PROJETO'],
                    value=self.bolsas[p['ID_PROJETO']],
                    _onchange='ajax("%s", ["%s"], "bolsasRet")' % (URL('adm', 'ajaxAlterarBolsas'), p['ID_PROJETO'])
                )
            else:
                return str(p["BOLSAS"])
        except KeyError:
            return "Indefinido"

    def observacao(self, projeto):
        avaliacao = current.db((current.db.avaliacao.id_projeto == projeto['ID_PROJETO'])
                               & (current.db.avaliacao.observacao != None)).select().first()
        if avaliacao:
            motivos = current.db(
                (current.db.avaliacao_respostas.pergunta == current.db.avaliacao_perguntas.id)
                & (current.db.avaliacao_respostas.resposta == True)
                & (current.db.avaliacao_respostas.avaliacao == avaliacao.id)).select(
                current.db.avaliacao_perguntas.pergunta)
            if motivos:
                return SPAN(
                    DIV(avaliacao.observacao, _class="alert alert-warning") if avaliacao.observacao else "",
                    SPAN(B("Quesitos não atendidos:")),
                    UL([LI(m.pergunta, _class='list-group-item') for m in motivos], _class='list-group')
                )
        return "Nenhuma observação."


class TableAcompanhamento(TableProjetos):
    def __init__(self, participacoes, projetos):
        super(TableAcompanhamento, self).__init__(projetos)
        self.headers = (
            "#",
            "Data de registro",
            "Num. Processo",
            "Título",
            "Função",
            "Situação",
            "Avaliação",
            "Qtd. Bolsas",
            "Arquivos",
            "Observação"
        )
        self.participacoes = participacoes

    def funcao(self, projeto):
        for i, dic in enumerate(self.participacoes):
            if dic["ID_PROJETO"] == projeto["ID_PROJETO"]:
                try:
                    return SIEParticipantesProjs().descricaoDeFuncaoDeParticipante(self.participacoes[i])
                except TypeError:
                    return 'Indefinido'

    def printTable(self):
        def row(p):
            return TR(p['ID_PROJETO'], p['DT_REGISTRO'], self.num_processo(p['NUM_PROCESSO']), p['TITULO'],
                      self.funcao(p),
                      self.situacao(p), self.avaliacao(p), self.bolsa(p), self.arquivos(p), self.observacao(p),
                      _id=p['ID_PROJETO'])

        return TABLE(
            THEAD(TR([TH(h) for h in self.headers])),
            TBODY([row(p) for p in self.projetos if p])
        )


class TableDeferimento(TableProjetos):
    def __init__(self, projetos):
        super(TableDeferimento, self).__init__(projetos)
        self.headers = (
            "#",
            "Coordenador",
            "Disciplina",
            "Título",
            "Qtd. Bolsas",
            "Avaliador",
            EMBED(_src=URL('static/images', 'delete.svg'), _width=24)
        )

    def removeBtn(self, p):
        return INPUT(_type='checkbox', _name='toDelete', _value=p['ID_PROJETO'], _class='delete')

    def printTable(self):
        def row(p):
            return TR(p['ID_PROJETO'], p['COORDENADOR'], self.disciplina(p), p['TITULO'], self.bolsa(p),
                      p['AVALIADOR'], self.removeBtn(p), _id=p['ID_PROJETO'])

        return FORM(
            TABLE(
                THEAD(TR([TH(h) for h in self.headers])),
                TBODY([row(p) for p in self.projetos if p])
            ),
            INPUT(_type='submit', _value='Remover projetos'),
            _onsubmit='removerSelecionadosDaTabela()'
        )


class TableAvaliacao(TableProjetos):
    def __init__(self, projetos):
        self.headers = (
            "#",
            "Coordenador",
            "Disciplina",
            "Arquivos",
            "Situação",
            "Avaliação",
            "Qtd. Bolsas",
            "Avaliar"
        )
        super(TableAvaliacao, self).__init__(projetos)

    def avaliar(self, projeto):
        if not SIEProjetos.isAvaliado(projeto):
            uniqueDOMid = "avaliar%d" % projeto["ID_PROJETO"]

            return SPAN(
                A("Aprovar", _id=projeto["ID_PROJETO"],
                  callback=URL('adm', 'aprovarAjax', vars={"ID_PROJETO": projeto["ID_PROJETO"]}),
                  target=uniqueDOMid),
                " | ",
                A("Reprovar", _id=projeto["ID_PROJETO"],
                  _href=URL('adm', 'avaliacaoPerguntas', vars={"ID_PROJETO": projeto["ID_PROJETO"]})),
                _id=uniqueDOMid
            )
        else:
            return self.avaliador(projeto)

    def printTable(self):
        def row(p):
            return TR(str(self.projetos.index(p) + 1), p['COORDENADOR'], self.disciplina(p), self.arquivos(p),
                      self.situacao(p), self.avaliacao(p), self.bolsa(p), self.avaliar(p), _id=p['ID_PROJETO'])

        return TABLE(
            THEAD(TR([TH(h) for h in self.headers])),
            TBODY([row(p) for p in self.projetos if p])
        )


class TableTransparenciaBolsistas(TableHelper):
    def __init__(self, content):
        """

        :type content: list
        """
        super(TableTransparenciaBolsistas, self).__init__()
        self.content = content
        self.headers = ('Número do processo', 'Disciplina', 'Valor', 'Coordenador', 'Bolsista')

    def printTable(self):
        def parsedRow(c):
            return TR(self.num_processo(c['NUM_PROCESSO']), self.disciplina(c), self.vl_bolsa(c['VL_BOLSA']),
                      c['COORDENADOR'], c['BOLSISTA'])

        return TABLE(
            THEAD(TR([TH(h) for h in self.headers])),
            TBODY([parsedRow(c) for c in self.content])
        )
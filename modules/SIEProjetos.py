# coding=utf-8
from datetime import date
from gluon import current
from unirio.api import UNIRIOAPIRequest
from SIEDocumento import SIEDocumentos


class Xpto(object):
    def __init__(self):
        self.api = UNIRIOAPIRequest(current.kAPIKey)


class SIEProjetos(Xpto):
    def __init__(self):
        super(SIEProjetos, self).__init__()
        self.path = "PROJETOS"


    def getProjetos(self):
        params = {
            'LMIN': 0,
            'LMAX': 20
        }
        fields = [
            'ID_PROJETO',
            'TITULO',
            'TIPO_PUBLICO_TAB',
            'TIPO_PUBLICO_ITEM',
            'DT_ALTERACAO'
        ]
        meuResultado = self.api.performGETRequest(self.path, params, fields)
        return meuResultado


    #TODO Corrigir TIPO_PUBLICO_ITEM após verificar com Alcides
    def salvarProjeto(self, projeto):
        """
        EVENTO_TAB              => Tipos de Eventos
        EVENTO_ITEM = 1         => Não se aplica
        TIPO_PUBLICO_TAB        => Público alvo
        TIPO_PUBLICO_ITEM = 1   => Geral

        :type projeto: gluon.storage.Storage
        :param projeto: Um projeto a ser inserido no banco
        :return: ID_PROJETO
        """
        novoDocumento = SIEDocumentos().criarDocumento()
        projeto.update({
            "ID_DOCUMENTO": novoDocumento.insertId,
            "EVENTO_TAB": 6028,
            "EVENTO_ITEM": 1,
            "TIPO_PUBLICO_TAB": 6002,
            "TIPO_PUBLICO_ITEM": 1,
            "ACESSO_PARTICIP": "S",
            "PAGA_BOLSA": "S",
            "DT_INICIAL": current.session.edicao.dt_inicial_projeto,
            "DT_REGISTRO": date.today()
        })
        novoProjeto = self.api.performPOSTRequest(self.path, projeto)
        return novoProjeto.insertId


class SIEClassificacoesPrj(Xpto):
    def __init__(self):
        super(SIEClassificacoesPrj, self).__init__()
        self.path = "CLASSIFICACOES_PRJ"

    def getClassificacoesPrj(self):
        """

        :rtype : list
        :return: Essa merda retorna blab lab la
        """
        params = {
            'CLASSIFICACAO_ITEM': 1,
            'CODIGO': 1
        }
        fields = [
            'ID_CLASSIFICACAO',
            'DESCRICAO'
        ]
        return self.api.performGETRequest(self.path, params, fields).content


class SIETramitacoes(Xpto):
    def __init__(self):
        super(SIETramitacoes, self).__init__()
        self.path = "TRAMITACOES"

    def criarTramitacao(self, documento):
        """
        SEQUENCIA = 1           => Primeiro passo da tramitação
        PRIORIDADE_TAB = 5101   => Tabela estruturada utilizada para indicar o nível de prioridade
        PRIORIDADE_ITEM = 2     => Prioridade normal
        SITUACAO_TRAMIT = T     => Indica que o documento não foi enviado ainda para tramitação
        IND_RETORNO_OBRIG = N   => Valor fixo, conforme documento da Síntese

        :param documento: Dicionário de dados de uma entra da tabela DOCUMENTOS
        """
        tramitacao = {
            "SEQUENCIA": 1,
            "ID_DOCUMENTO": documento["ID_DOCUMENTO"],
            "TIPO_ORIGEM": documento["TIPO_PROPRIETARIO"],
            "ID_ORIGEM": documento["ID_PROPRIETARIO"],
            "TIPO_DESTINO": documento["TIPO_PROPRIETARIO"],
            "ID_DESTINO": documento["ID_PROPRIETARIO"],
            "DT_ENVIO": date.today(),
            "SITUACAO_TRAMIT": "T",
            "IND_RETORNO_OBRIG": "N",
            "PRIORIDADE_TAB": 5101,
        }

        return self.api.performPOSTRequest(self.path, tramitacao)


class SIEParticipantesProjs(Xpto):
    def __init__(self):
        super(SIEParticipantesProjs, self).__init__()
        self.path = "PARTICIPANTES_PROJ"

    def criarParticipante(self, ID_PROJETO):
        participante = {
            "ID_PROJETO": ID_PROJETO,
            "FUNCAO_TAB": "",
            "FUNCAO_ITEM": "",
            "CARGA_HORARIA": 0,
            "TITULACAO_TAB": "",
            "TITULACAO_ITEM": "",
            "SITUACAO": "",
            "CH_SUGERIDA": 0
        }

        return self.api.performPOSTRequest(self.path, participante)

# coding=utf-8
from datetime import date

from sie import SIE
from gluon import current
from sie.SIEDocumento import SIEDocumentos
from sie.SIEFuncionarios import SIEFuncionarios

__all__ = [
    "SIEProjetos",
    "SIEClassificacoesPrj",
    "SIEParticipantesProjs",
    "SIECursosDisciplinas",
    "SIEClassifProjetos"
]


class SIEProjetos(SIE):
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
    def salvarProjeto(self, projeto, funcionario):
        """
        EVENTO_TAB              => Tipos de Eventos
        EVENTO_ITEM = 1         => Não se aplica
        TIPO_PUBLICO_TAB        => Público alvo
        TIPO_PUBLICO_ITEM = 1   => Geral

        :type projeto: gluon.storage.Storage
        :param projeto: Um projeto a ser inserido no banco
        :return: Um dicionário contendo a entrada uma nova entrada da tabela PROJETOS
        """
        novoDocumento = SIEDocumentos().criarDocumento(funcionario)
        projeto.update({
            "ID_DOCUMENTO": novoDocumento["ID_DOCUMENTO"],
            "NUM_PROCESSO": novoDocumento["NUM_PROCESSO"],
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
        projeto.update({"ID_PROJETO": novoProjeto.insertId})

        return projeto


class SIEClassificacoesPrj(SIE):
    def __init__(self):
        super(SIEClassificacoesPrj, self).__init__()
        self.path = "CLASSIFICACOES_PRJ"

    def getClassificacoesPrj(self, classificacaoItem, codigo):
        """
        CLASSIFICACAO_ITEM  => 1 - Tipos de Projetos, 41 - Disciplina vinculada
        CODIGO PARA CLASSIFICACAO_ITEM = 1 => 1 - Ensino, 2 - Pesquisa, 3 - Extensão, 4 - Desenvolvimento institucional

        :rtype : list
        :return: Uma lista de dicionários com os tipos de projetos
        """
        params = {
            'CLASSIFICACAO_ITEM': classificacaoItem,
            'CODIGO': codigo
        }
        fields = [
            'ID_CLASSIFICACAO',
            'DESCRICAO'
        ]
        return self.api.performGETRequest(self.path, params, fields).content


class SIEParticipantesProjs(SIE):
    def __init__(self):
        super(SIEParticipantesProjs, self).__init__()
        self.path = "PARTICIPANTES_PROJ"

    def criarParticipante(self, ID_PROJETO, funcionario):
        """
        FUNCAO_TAB = 6003       => Papel do participante de um projeto
        FUNCAO_ITEM = 1         => Coordenador
        SITUACAO = A            => Ao adicionar um participante, ele estará ativo(A)

        :rtype : unirio.api.apiresult.APIPostResponse
        :param ID_PROJETO: Identificador único de uma entrada na tabela PROJETOS
        :param funcionario: Dicionário de IDS de um funcionário
        :return:
        """
        escolaridade = SIEFuncionarios().getEscolaridade(funcionario["ID_FUNCIONARIO"])
        participante = {
            "ID_PROJETO": ID_PROJETO,
            "FUNCAO_TAB": 6003,
            "FUNCAO_ITEM": 1,
            "CARGA_HORARIA": 0,
            "TITULACAO_TAB": escolaridade["ESCOLARIDADE_TAB"],
            "TITULACAO_ITEM": escolaridade["ESCOLARIDADE_ITEM"],
            "SITUACAO": "A",
            "CH_SUGERIDA": 0
        }

        return self.api.performPOSTRequest(self.path, participante)


class SIECursosDisciplinas(SIE):
    def __init__(self):
        super(SIECursosDisciplinas, self).__init__()
        self.path = "V_CURSOS_DISCIPLINAS"

    def getCursos(self):
        params = {
            "LMIN": 0,
            "LMAX": 99999,
            "ORDERBY": "NOME_CURSO",
            "DISTINCT": "NOME_CURSO"
        }
        fields = [
            "NOME_CURSO",
            "ID_CURSO"
        ]
        return self.api.performGETRequest(self.path, params, fields).content


    def getDisciplinas(self, curso, filtroObrigatorias=False):
        params = {
            "LMIN": 0,
            "LMAX": 9999,
            "ID_CURSO": curso,
            "ORDERBY": "NOME_DISCIPLINA"
        }
        if filtroObrigatorias:
            params["OBRIGATORIA"] = "S"
        fields = [
            "NOME_DISCIPLINA",
            "COD_DISCIPLINA"
        ]
        return self.api.performGETRequest(self.path, params, fields).content


class SIEClassifProjetos(SIE):
    def __init__(self):
        super(SIEClassifProjetos, self).__init__()
        self.path = "CLASSIF_PROJETOS"

    #TODO verificar pois não está inserindo ainda
    def criarClassifProjetos(self, ID_PROJETO, ID_CLASSIFICACAO):
        classifProj = {
            "ID_PROJETO": ID_PROJETO,
            "ID_CLASSIFICACAO": ID_CLASSIFICACAO
        }

        try:
            return self.api.performPOSTRequest(self.path, classifProj)
        except Exception:
            current.session.flash = "Não foi possível criar uma nova classificação para o projeto."
# coding=utf-8
import base64
from datetime import date
from sie import SIE
from gluon import current
from sie.SIEDocumento import SIEDocumentos
from sie.SIEFuncionarios import SIEFuncionarios

__all__ = [
    "SIEProjetos",
    "SIEArquivosProj",
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
        :type funcionario: dict
        :param funcionario: Dicionário de IDS de um funcionário
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


class SIEArquivosProj(SIE):
    def __init__(self):
        super(SIEArquivosProj, self).__init__()
        self.path = "ARQUIVOS_PROJ"

    def salvarArquivo(self, arquivo, projeto, funcionario):
        """


        :type arquivo: FieldStorage
        :param arquivo: Um arquivo correspondente a um projeto que foi enviado para um formulário
        :type projeto: dict
        :param projeto: Um dicionário contendo uma entrada da tabela PROJETOS
        :type funcionario: dict
        :param funcionario: Dicionário de IDS de um funcionário
        :rtype : dict
        """
        arquivoProj = {
            "ID_PROJETO": projeto["ID_PROJETO"],
            "DT_INCLUSAO": date.today(),
            "TIPO_ARQUIVO_TAB": 6005,
            "TIPO_ARQUIVO_ITEM": 99999, # TODO Verificar qual é o item correto
            "NOME_ARQUIVO": arquivo.filename,
            "CONTEUDO_ARQUIVO": base64.b64encode(arquivo.file.read()),
            "ID_AVALIACAO_PROJETO": 99999 # TODO Verificar o que é e se deve ou não ser preenchido
        }

        novoArquivoProj = self.api.performPOSTRequest(self.path, arquivoProj)
        arquivoProj.update({"ID_ARQUIVO_PROJ": novoArquivoProj.insertId})

        return arquivoProj

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
        """

        :type ID_PROJETO: int
        :param ID_PROJETO: Identificador único de um projeto
        :type ID_CLASSIFICACAO: int
        :param ID_CLASSIFICACAO: Identificador único da classificação de um projeto
        :rtype: unirio.api.apiresult.APIPOSTResponse
        """
        classifProj = {
            "ID_PROJETO": ID_PROJETO,
            "ID_CLASSIFICACAO": ID_CLASSIFICACAO
        }

        try:
            return self.api.performPOSTRequest(self.path, classifProj)
        except Exception:
            current.session.flash = "Não foi possível criar uma nova classificação para o projeto."
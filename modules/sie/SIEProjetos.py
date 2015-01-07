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
    "SIEClassifProjetos",
    "SIEOrgaosProjetos"
]


class SIEProjetos(SIE):
    def __init__(self):
        super(SIEProjetos, self).__init__()
        self.path = "PROJETOS"

    def getProjeto(self, ID_PROJETO):
        params = {
            'LMIN': 0,
            'LMAX': 1,
            'ID_PROJETO': ID_PROJETO
        }

        try:
            return self.api.performGETRequest(self.path, params, cached=self.cacheTime).content[0]
        except (ValueError, AttributeError):
            return None


    def getProjetos(self, params={}):
        params.update({
            'LMIN': 0,
            'LMAX': 20
        })
        fields = [
            'ID_PROJETO',
            'TITULO',
            'TIPO_PUBLICO_TAB',
            'TIPO_PUBLICO_ITEM',
            'DT_ALTERACAO'
        ]
        meuResultado = self.api.performGETRequest(self.path, params, fields)
        return meuResultado


    def salvarProjeto(self, projeto, funcionario):
        """
        EVENTO_TAB              => Tipos de Eventos
        EVENTO_ITEM = 1         => Não se aplica
        TIPO_PUBLICO_TAB        => Público alvo
        TIPO_PUBLICO_ITEM = 8   => 3o grau

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
            "TIPO_PUBLICO_ITEM": 8,
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

    def __conteudoDoArquivo(self, arquivo):
        """
        O campo CONTEUDO_ARQUIVO é BLOB, tendo em vista que a API espera uma string base64, o método é responsável por
        encodar o conteúdo e fornecer uma string válida

        :type arquivo: file
        :rtype : str
        :param arquivo: Um arquivo a ser convertido
        :return: Uma string correspondente ao conteúdo de um arquivo binário, na forma de base64
        """
        return base64.b64encode(arquivo.file.read())

    def salvarArquivo(self, arquivo, projeto, funcionario):
        """

        TIPO_ARQUIVO_ITEM = 1       => Projeto

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
            "TIPO_ARQUIVO_ITEM": 1,
            "NOME_ARQUIVO": arquivo.filename,
            "CONTEUDO_ARQUIVO": self.__conteudoDoArquivo(arquivo)
        }

        novoArquivoProj = self.api.performPOSTRequest(self.path, arquivoProj)
        arquivoProj.update({"ID_ARQUIVO_PROJ": novoArquivoProj.insertId})

        self.salvarCopiaLocal(arquivo, arquivoProj, funcionario)

        return arquivoProj

    def salvarCopiaLocal(self, arquivo, arquivoProj, funcionario):
        """

        :type arquivo: FieldStorage
        :param arquivo: Um arquivo correspondente a um projeto que foi enviado para um formulário
        :type arquivo_proj: dict
        :param arquivo_proj: Um dicionário contendo uma entrada da tabela ARQUIVO_PROJS
        :type funcionario: dict
        :param funcionario: Dicionário de IDS de um funcionário
        """
        try:
            current.db.projetos.insert(
                anexo_tipo=arquivo.type,
                id_arquivo_proj=arquivoProj["ID_ARQUIVO_PROJ"],
                id_funcionario=funcionario["ID_FUNCIONARIO"]
            )
        except:
            current.db.rollback()
            raise Exception("Não foi possível salver o arquivo %s do projeto localmente" % arquivo.filename)
        finally:
            current.db.commit()


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
        return self.api.performGETRequest(self.path, params, fields, cached=self.cacheTime).content


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
            "CARGA_HORARIA": 0,  # TODO Perguntar qual é a carga horária correta
            "TITULACAO_TAB": escolaridade["ESCOLARIDADE_TAB"],
            "TITULACAO_ITEM": escolaridade["ESCOLARIDADE_ITEM"],
            "SITUACAO": "A",
            "CH_SUGERIDA": 0,  # TODO Perguntar qual é a carga horária correta
            "ID_PESSOA": funcionario["ID_PESSOA"],
            "ID_CONTRATO_RH": funcionario["ID_CONTRATO_RH"],
        }

        return self.api.performPOSTRequest(self.path, participante)

    def getParticipacoes(self, funcionario):
        params = {
            "ID_PESSOA": funcionario["ID_PESSOA"],
            "LMIN": 0,
            "LMAX": 9999
        }
        fields = ["ID_PROJETO", "FUNCAO_ITEM"]
        return self.api.performGETRequest(self.path, params, fields, self.cacheTime)


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


    def getDisciplinas(self, ID_CURSO, filtroObrigatorias=False):
        params = {
            "LMIN": 0,
            "LMAX": 9999,
            "ID_CURSO": ID_CURSO,
            "ORDERBY": "NOME_DISCIPLINA"
        }
        if filtroObrigatorias:
            params["OBRIGATORIA"] = "S"
        fields = [
            "NOME_DISCIPLINA",
            "COD_DISCIPLINA"
        ]
        return self.api.performGETRequest(self.path, params, fields).content

    def getIdUnidade(self, ID_CURSO):
        params = {
            "ID_CURSO": ID_CURSO
        }
        fields = ["ID_UNIDADE"]
        return self.api.performGETRequest(self.path, params, fields).content[0]["ID_UNIDADE"]


class SIEClassifProjetos(SIE):
    def __init__(self):
        super(SIEClassifProjetos, self).__init__()
        self.path = "CLASSIF_PROJETOS"

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


class SIEOrgaosProjetos(SIE):
    def __init__(self):
        super(SIEOrgaosProjetos, self).__init__()
        self.path = "ORGAOS_PROJETOS"

    def criarOrgaosProjetos(self, projeto, ID_UNIDADE):
        """
        FUNCAO_ORG_TAB => 6006 - Função dos órgãos nos projetos
        FUNCAO_ITEM_TAB => 6 - Curso beneficiado

        :param projeto:
        :param ID_UNIDADE:
        :return:
        """
        orgaoProj = {
            "ID_PROJETO": projeto["ID_PROJETO"],
            "ID_UNIDADE": ID_UNIDADE,
            "FUNCAO_ORG_TAB": 6006,
            "FUNCAO_ORG_ITEM": 6,
            "DT_INICIAL": projeto["DT_INICIAL"],
            "SITUACAO": "A"
        }
        try:
            return self.api.performPOSTRequest(self.path, orgaoProj)
        except Exception:
            current.session.flash = "Não foi possível associar um órgão ao projeto."
# coding=utf-8
from datetime import date
from SIEProjetos import Xpto
from gluon import current


class SIEDocumentos(Xpto):
    ID_TIPO_DOC = 215
    def __init__(self):
        super(SIEDocumentos, self).__init__()
        self.path = "DOCUMENTOS"

    def proximoNumeroProcesso(self):
        """
        Número do processo é formado através da concatenação de um ID_TIPO_DOC, um sequencial e o ano do documento

        :rtype : str
        :return: Retorna o NUM_PROCESSO gerado a partir da lógica de negócio
        """
        ano = current.session.edicao.dt_inicial_projeto.year
        numeroTipoDoc = SIENumeroTipoDocumento(ano, self.ID_TIPO_DOC)

        NUM_ULTIMO_DOC = str(numeroTipoDoc.proximoNumeroTipoDocumento()).zfill(4)
        return "%d%s/%d" % (self.ID_TIPO_DOC, NUM_ULTIMO_DOC, ano)

    def criarDocumento(self, funcionario):
        """
        ID_TIPO_DOC = 215       => Projetos de Ensino
        SITUACAO_ATUAL = 1      => Um novo documento sempre se inicia com 1
        TIPO_PROPRIETARIO = 20  => Indica restrição de usuários
        TIPO_ORIGEM = 20        => Recebe mesmo valor de TIPO_PROPRIETARIO
        SEQUENCIA = 1           => Indica que é o primeiro passo de tramitação
        TIPO_PROCEDENCIA = S    => Indica servidor
        TIPO_INTERESSADO = S    => Indica servidor

        IND_ELIMINADO, IND_AGENDAMENTO, IND_RESERVADO,
        IND_EXTRAVIADO, TEMPO_ESTIMADO => Valores fixos (Seguimos documento com recomendações da síntese)

        :rtype : unirio.api.APIPOSTResponse
        :return:
        """
        documento = {
            "ID_TIPO_DOC": 215,
            "ID_PROCEDENCIA": funcionario["ID_CONTRATO_RH"],
            "ID_PROPRIETARIO": funcionario["ID_USUARIO"],
            "ID_CRIADOR": funcionario["ID_USUARIO"],
            "NUM_PROCESSO": self.proximoNumeroProcesso(),
            "TIPO_PROCEDENCIA": "S",
            "TIPO_INTERESSADO": "S",
            "ID_INTERESSADO": funcionario["ID_CONTRATO_RH"],
            "SITUACAO_ATUAL": 1,
            "TIPO_PROPRIETARIO": 20,
            "TIPO_ORIGEM": 20,
            "DT_CRIACAO": date.today(),
            "IND_ELIMINADO": "N",
            "IND_AGENDAMENTO": "N",
            "IND_RESERVADO": "N",
            "IND_EXTRAVIADO": "N",
            "TEMPO_ESTIMADO": 1,
            "SEQUENCIA": 1
        }

        return self.api.performPOSTRequest(self.path, documento)


class SIENumeroTipoDocumento(Xpto):
    def __init__(self, ano, ID_TIPO_DOC):
        super(SIENumeroTipoDocumento, self).__init__()
        self.path = "NUMEROS_TIPO_DOC"
        self.ano = ano
        self.ID_TIPO_DOC = ID_TIPO_DOC

    def proximoNumeroTipoDocumento(self):
        params = {
            "ID_TIPO_DOC": self.ID_TIPO_DOC,
            "ANO_TIPO_DOC": self.ano
        }
        fields = ["ID_NUMERO_TIPO_DOC", "NUM_ULTIMO_DOC"]
        try:
            numero_tipo_doc = self.api.performGETRequest(self.path, params, fields)
            ID_NUMERO_TIPO_DOC = numero_tipo_doc.content[0]["ID_NUMERO_TIPO_DOC"]
            numero = numero_tipo_doc.content[0]["NUM_ULTIMO_DOC"] + 1
            try:
                self.atualizarTotalNumeroUltimoDocumento(ID_NUMERO_TIPO_DOC, numero)
            except Exception as e:
                raise e
        except ValueError:
            self.atualizarIndicadoresDefault()
            numero = self.criarNovoNumeroTipoDocumento()

        return numero

    def atualizarIndicadoresDefault(self):
        numerosDocumentos = self.api.performGETRequest(
            self.path,
            {"ID_TIPO_DOC": self.ID_TIPO_DOC},
            ["ID_NUMERO_TIPO_DOC"]
        )
        for numero in numerosDocumentos.content:
            self.api.performPUTRequest(
                self.path,
                {
                    "ID_NUMERO_TIPO_DOC": numero["ID_NUMERO_TIPO_DOC"],
                    "IND_DEFAULT": "N"
                }
            )
            print numero["ID_NUMERO_TIPO_DOC"]

    def atualizarTotalNumeroUltimoDocumento(self, ID_NUMERO_TIPO_DOC, numero):
        self.api.performPUTRequest(
            self.path,
            {
                "ID_NUMERO_TIPO_DOC": ID_NUMERO_TIPO_DOC,
                "NUM_ULTIMO_DOC": numero
             }
        )

    def criarNovoNumeroTipoDocumento(self):
        """

        NUM_ULTIMO_DOC retorna 1 para que não seja necessário chamar novo método para atualizar
        :rtype : int
        :return: NUM_ULTIMO_DOC da inserção
        """
        NUM_ULTIMO_DOC = 1
        params = {
            "ID_TIPO_DOC": self.ID_TIPO_DOC,
            "ANO_TIPO_DOC": self.ano,
            "IND_DEFAULT": "S",
            "NUM_ULTIMO_DOC": NUM_ULTIMO_DOC
        }
        self.api.performPOSTRequest(self.path, params)
        return NUM_ULTIMO_DOC

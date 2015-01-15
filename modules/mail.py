# coding=utf-8
from gluon import current


class MailAvaliacao(object):
    def __init__(self, avaliacao):
        """
        A classe ``MailAvaliacao``trata estritamente de envio de emails relacionados aos estágios de uma avaliação.
        Utilizada a classe nativa de email de gluon.tools.

        :type avaliacao: Avaliacao
        :param avaliacao: Uma avaliação referente ao email
        """
        self.avaliacao = avaliacao
        self.reply_to = "naoresponser.projetos@unirio.br"
        self.subject = "[DTIC/PROGEP] Avaliação Funcional e Institucional de " + self.avaliacao.servidorAvaliado["NOME_SERVIDOR"].encode('utf-8')
        self.footer = "**** E-MAIL AUTOMÁTICO - NÃO RESPONDA ****"

    #TODO Verificar se não é possivel pegar algum erro caso o email não seja enviado
    def sendConfirmationEmail(self):
        professor = self.parametrosParaAvaliacaoProfessor

        current.mail.send(**professor)

    @property
    def parametrosParaAvaliacaoProfessor(self):
        """
        Email a ser enviado para o servidor ao término de uma avaliação.

        :rtype : dict
        :return: Dicionário de parâmetros de email
        """
        return {
            "to": [self.avaliacao.servidorAvaliado['EMAIL_SERVIDOR']],
            "subject": self.subject,
            "reply_to": self.reply_to,
            "message": "Prezado professor, seu projeto foi avaliado. O resultado da avaliação ja está disponível em: " +
            " "
        }

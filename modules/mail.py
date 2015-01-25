# coding=utf-8
from gluon import current


class MailAvaliacao(object):
    def __init__(self, coordenador):
        """
        A classe ``MailAvaliacao``trata estritamente de envio de emails relacionados aos estágios de uma avaliação.
        Utilizada a classe nativa de email de gluon.tools.

        :type avaliacao: Avaliacao
        :param avaliacao: Uma avaliação referente ao email
        """

        self.to = coordenador["DESCR_MAIL"]
        self.reply_to = current.mail.settings.sender
        self.subject = "[DTIC/PROGRAD] Avaliação de projeto de Ensino"
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
            "to": self.to,
            "subject": self.subject,
            "reply_to": self.reply_to,
            "message": "Prezado professor, seu projeto foi avaliado. O resultado da avaliação ja está disponível em: " +
            "http://sistemas.unirio.br/projetos_ensino/consulta"
        }

# coding=utf-8
from sie import SIE

__all__ = ["SIEAlunos"]


class SIEAlunos(SIE):
    def __init__(self):
        super(SIEAlunos, self).__init__()
        self.path = "ALUNOS"

    def getCRA(self, ID_ALUNO):
        """
        O cálculo do coeficiente de rendimento acumulado é calculado pela expressão S (Di × Ci) / S Ci onde Di é a nota
        final da disciplina “i”; Ci é o crédito atribuído à disciplina “i”. Assim, o CRa do aluno é a somatório dos
        produtos das notas da disciplina pelo seu respectivo crédito, dividido pelo somatório dos créditos acumulados
        até o período em curso. O CRa é critério indispensável e fundamental nos concursos de bolsas.

        Referência: Manual do Aluno - UNIRIO

        :type ID_ALUNO: int
        :param ID_ALUNO: Idenficador único de um aluno na tabela ALUNOS
        :return: O coeficiente de rendimento acumulado deste aluno
        :rtype : dict
        """
        return self.api.performGETRequest("V_COEF_REND_ACAD", {"ID_ALUNO": ID_ALUNO}, cached=self.cacheTime).content[0]

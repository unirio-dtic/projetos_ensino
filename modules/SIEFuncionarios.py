from SIEProjetos import Xpto


class SIEFuncionarioID(Xpto):
    def __init__(self, CPF):
        super(SIEFuncionarioID, self).__init__()
        self.path = "V_FUNCIONARIO_IDS"
        self.CPF = CPF

    def getFuncionarioIDs(self):
        return self.api.performGETRequest(self.path, params={"CPF": self.CPF}).content[0]
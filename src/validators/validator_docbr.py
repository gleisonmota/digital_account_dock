from validate_docbr import CPF, CNPJ

class Validator_docbr:
    def __init__(self, document, type_document):
        self.type_document = type_document
        document = str(document)
        if self.type_document == 'cpf':
            if self.cpf_is_valid(document):
                self.cpf = document
            else:
                raise ValueError('CPF inválido.')
        elif self.type_document == 'cnpj':
            if self.cnpj_is_valid(document):
                self.cnpj = document
            else:
                raise ValueError('CNPJ inválido.')
        else:
            raise ValueError('Documento inválido.')

        
    def cpf_is_valid(self, cpf):
        if len(cpf) == 11:
            validate_cpf =  CPF()
            return validate_cpf.validate(cpf)
        else:
            raise ValueError('Quantidade de dígitos inválida.')


    def cnpj_is_valid(self, cnpj):
        if len(cnpj) == 14:
            validate_cnpj = CNPJ()
            return validate_cnpj.validate(cnpj)
        else:
            raise ValueError('Quantidade de dígitos inválida.')
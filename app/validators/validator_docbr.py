from validate_docbr import CPF, CNPJ

class Validator_docbr:
    def __init__(self, document, type_document):
        self.type_document = type_document
        document = str(document)
        if self.type_document == 'cpf':
            if not self.cpf_is_valid(document):
                raise ValueError('CPF inválido.')
            self.cpf = document

        elif self.type_document == 'cnpj':
            if not self.cnpj_is_valid(document):
                raise ValueError('CNPJ inválido.')
            self.cnpj = document

        else:
            raise ValueError('Documento inválido.')

        
    def cpf_is_valid(self, cpf):
        cpf = str(cpf).replace('.', '').replace('-', '')
        if len(cpf) != 11:
            raise ValueError('CPF inválido')
        validate_cpf =  CPF()
        return validate_cpf.validate(cpf)


    def cnpj_is_valid(self, cnpj):
        cnpj = str(cnpj).replace('.', '').replace('/', '').replace('-', '')
        if len(cnpj) != 14:
            raise ValueError('CNPJ inválido.')
        validate_cnpj = CNPJ()
        return validate_cnpj.validate(cnpj)
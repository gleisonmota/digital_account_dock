
-- select * from transacoes
select * from contas
-- ORDER BY conta ASC


-- ----------TABLE contas
-- CREATE TABLE contas(conta SERIAL PRIMARY KEY, 
-- agencia VARCHAR(10),
-- cpf VARCHAR(11),
-- portador VARCHAR(100),
-- status_conta VARCHAR(20),
-- saldo INTEGER default 0,
-- limite INTEGER default 2000,
-- data_abertura_conta TIMESTAMP
-- --saque INTEGER DEFAULT 0,
-- --deposito INTEGER DEFAULT 0,
-- --tipo_transacao VARCHAR(20),
-- )

-- INSERT INTO contas(agencia, cpf, portador, status_conta, saldo, limite, data_abertura_conta)
-- VALUES('1213', '01234567890', 'Fred', 'bloqueada', DEFAULT, 2000, localtimestamp);



-- CREATE TABLE transacoes(id SERIAL PRIMARY KEY,
-- conta INTEGER, 
-- agencia VARCHAR(10),
-- cpf VARCHAR(11),
-- portador VARCHAR(100),
-- tipo_transacao VARCHAR(20),
-- data_transacao TIMESTAMP,
-- valor_saque INTEGER DEFAULT 0,
-- valor_deposito INTEGER DEFAULT 0,
-- saldo INTEGER DEFAULT 0
-- )

-- INSERT INTO transacoes(conta, agencia, cpf, portador, tipo_transacao, data_transacao, valor_saque, valor_deposito, saldo)
-- VALUES(DEFAULT, '1213', '01234567890', 'Fred', 'deposito', localtimestamp, DEFAULT, 5000, 5000);


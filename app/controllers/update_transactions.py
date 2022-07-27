import pandas as pd
from flask import Blueprint, Response, request
from app.repositories.server import ConnectionDb
from app.validators.validator_docbr import Validator_docbr
from datetime import datetime
import sys, os
import json

dirName, ___DUMMY = os.path.split(os.path.abspath(__file__))
sys.path.append(os.path.join(dirName))

config = json.loads(open(dirName + "\\..\\templates\\config.json", "r", encoding="utf-8").read())

host = config["db_host"]
dbname = config["db_dbname"]
user = config["db_user"]
psw = config["db_password"]

connection = ConnectionDb(host, dbname, user, psw)

blueprint = Blueprint("update_transactions", __name__)

columns_accounts = [
                    'conta',
                    'agencia',
                    'cpf',
                    'portador',
                    'status_conta',
                    'saldo',
                    'limite',
                    'data_abertura_conta'
                    ]

@blueprint.route("/transacoes/saque/<conta>", methods=["PUT"])
def withdrawal_transaction(conta):
    date_now = datetime.today()
    DATA_TRANSACAO = [date_now.strftime('%Y-%m-%d %H:%M:%S')]
    limite = 2000
    conn = connection.postgre_sql()
    try:
        sql_saldo = """select * from contas 
                    where conta = '{}' """
        conn.execute(sql_saldo.format(conta))
        data = pd.DataFrame(conn, columns=columns_accounts)
        # saldo_total = request.json["deposito"] + data["saldo"][0]
        if data["saldo"][0] < 0:
            return Response(json.dumps({"mensagem": "Saldo negativo"}))
        saldo_total = data["saldo"][0] - request.json["valor_saque"]

        if request.json["status_conta"] != "ativa": #Só é possível realizar transação com a conta ativa
            return Response(json.dumps({"mensagem": "Conta nao ativa"}))
        # if not request.json["limite"] > limite: #limite máximo 2.000
        #     return Response(json.dumps({"mensagem": "Limite nao liberado, maximo de R$ 2000"}))
        if request.json["tipo_transacao"] not in ("saque"):
            return Response(json.dumps({"mensagem": "transcao nao efetuada"}))
        if Validator_docbr(str(request.json["cpf"]).zfill(11).replace('.0', ''), 'cpf'): #valida cpf 
            if not request.json["valor_saque"] <= saldo_total: #não realiza saque se o valor solicitado for maior que o saldo
                return Response(json.dumps({"mensagem": "saldo insuficiente"}))
            sql_transacoes="""
                UPDATE contas SET saldo = {}
                WHERE conta = '{}'
                """.format(
                            saldo_total,
                            conta
                            )
            conn.execute(sql_transacoes)
            conn.connection.commit()

            sql_extrato="""
                INSERT INTO transacoes(conta, agencia, cpf, portador, tipo_transacao, data_transacao, valor_saque, saldo)
                VALUES('{}', '{}', '{}', '{}', '{}', '{}', {}, {})
                """.format(
                            data["conta"][0], 
                            request.json["agencia"], 
                            request.json["cpf"], 
                            request.json["portador"], 
                            request.json["tipo_transacao"],
                            DATA_TRANSACAO[0],
                            request.json["valor_saque"],
                            saldo_total
                                    )
            conn.execute(sql_extrato)
            conn.connection.commit()
            return Response(json.dumps({"mensagem": "transacao efetuada"}))

    except Exception as e:
        if e.args[0] == 'CPF inválido.':
            return Response(json.dumps({"mensagem": "CPF invalido"}))
        return Response(json.dumps({"mensagem": "Error"}))

@blueprint.route("/transacoes/deposito/<conta>", methods=["put"])
def deposit_transaction(conta):
    date_now = datetime.today()
    DATA_TRANSACAO = [date_now.strftime('%Y-%m-%d %H:%M:%S')]
    limite = 2000
    conn = connection.postgre_sql()
    try:
        sql_saldo = """select * from contas 
                    where conta = '{}' """
        conn.execute(sql_saldo.format(conta))
        data = pd.DataFrame(conn, columns=columns_accounts)
        saldo_total = request.json["valor_deposito"] + data["saldo"][0]

        if request.json["status_conta"] != "ativa": #Só é possível realizar transação com a conta ativa
            return Response(json.dumps({"mensagem": "Conta nao ativa"}))

        if request.json["tipo_transacao"] not in ("deposito"):
            return Response(json.dumps({"mensagem": "transacao nao efetuada - selecione deposito como tipo de transacao"}))

        if Validator_docbr(str(request.json["cpf"]).zfill(11).replace('.0', ''), 'cpf'): #valida cpf 
            sql_transacoes="""
                UPDATE contas SET saldo = '{}'
                WHERE conta = '{}'
                """.format(
                            saldo_total,
                            conta
                            )
            conn.execute(sql_transacoes)
            conn.connection.commit()

            sql_extrato="""
                INSERT INTO transacoes(conta, agencia, cpf, portador, tipo_transacao, data_transacao, valor_deposito, saldo)
                VALUES('{}', '{}', '{}', '{}', '{}', '{}', {}, {})
                """.format(
                            data["conta"][0], 
                            request.json["agencia"], 
                            request.json["cpf"], 
                            request.json["portador"], 
                            request.json["tipo_transacao"],
                            DATA_TRANSACAO[0],
                            request.json["valor_deposito"], 
                            saldo_total
                                    )
            conn.execute(sql_extrato)
            conn.connection.commit()
            return Response(json.dumps({"mensagem": "transacao efetuada"}))

    except Exception as e:
        if e.args[0] == 'CPF inválido.':
            return Response(json.dumps({"mensagem": "CPF invalido"}))
        return Response(json.dumps({"mensagem": "Error"}))
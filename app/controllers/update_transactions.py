import pandas as pd
from flask import Blueprint, Response, request, make_response
from app.repositories.connection_db import ConnectionDb
from app.templates.http_status_codes import HTTP_404_NOT_FOUND
from app.templates.http_status_codes import HTTP_405_METHOD_NOT_ALLOWED
from app.validators.validator_docbr import Validator_docbr
from app.validators.error_response import ErrorResponse
from http import HTTPStatus
from datetime import datetime
import sys
import os
import json

dirName, ___DUMMY = os.path.split(os.path.abspath(__file__))
sys.path.append(os.path.join(dirName))

config = json.loads(
    open(dirName + "\\..\\templates\\config.json", "r", encoding="utf-8").read())

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


@blueprint.route("/transacoes/saque/<conta>", methods=["POST"])
def withdrawal_transaction(conta):
    date_now = datetime.today()
    transaction_date = [date_now.strftime('%Y-%m-%d %H:%M:%S')]
    conn = connection.postgre_sql()
    try:
        sql_saldo = """select * from contas 
                    where conta = '{}' """
        conn.execute(sql_saldo.format(conta))
        data = pd.DataFrame(conn, columns=columns_accounts)

        if data['status_conta'][0] != "Ativa":
            error_response = ErrorResponse(
                "Conta está desativada", HTTPStatus.BAD_REQUEST)
            return error_response.__handler_response__()

        if data["saldo"][0] < 0:
            if request.json["valor_saque"] > data['limite'][0]:
                error_response = ErrorResponse(
                    "Saldo insuficiente", HTTPStatus.BAD_REQUEST)
                return error_response.__handler_response__()
            else:
                limit = data['limite'][0] - request.json["valor_saque"]
                balance = data["saldo"][0] - request.json["valor_saque"]

        else:
            if request.json["valor_saque"] > (data['limite'][0] + data["saldo"][0]):
                error_response = ErrorResponse(
                    "Saldo insuficiente", HTTPStatus.BAD_REQUEST)
                return error_response.__handler_response__()
            else:
                if request.json["valor_saque"] > data["saldo"][0]:
                    if not (request.json["valor_saque"] - data["saldo"][0]) > data['limite'][0]:
                        if request.json["valor_saque"] > data["saldo"][0]:
                            used_limit = data["saldo"][0] - \
                                request.json["valor_saque"]
                            balance = used_limit
                            limit = data['limite'][0] - used_limit * -1
                        else:
                            balance = data["saldo"][0] - \
                                request.json["valor_saque"]
                            limit = data['limite'][0]
                else:
                    balance = data["saldo"][0] - \
                        request.json["valor_saque"]
                    limit = data['limite'][0]

        if Validator_docbr(request.json["cpf"], 'cpf'):
            sql_transacoes = """
                UPDATE contas SET saldo = {}, limite = {}
                WHERE conta = '{}'
                """.format(
                balance,
                limit,
                conta
            )
            conn.execute(sql_transacoes)
            conn.connection.commit()

            sql_extrato = """
                INSERT INTO transacoes(conta, agencia, cpf, portador, tipo_transacao, data_transacao, valor_saque, saldo)
                VALUES('{}', '{}', '{}', '{}', '{}', '{}', {}, {})
                """.format(
                data["conta"][0],
                request.json["agencia"],
                request.json["cpf"],
                request.json["portador"],
                "saque",
                transaction_date[0],
                request.json["valor_saque"],
                balance
            )
            conn.execute(sql_extrato)
            conn.connection.commit()
            return Response(json.dumps({"mensagem": "transacao efetuada"}))

    except Exception as e:
        error_response = ErrorResponse(
            e.args[0], HTTPStatus.BAD_REQUEST)
        return error_response.__handler_response__()
    error_response = ErrorResponse("Error", HTTPStatus.BAD_REQUEST)
    return error_response.__handler_response__()


@blueprint.route("/transacoes/deposito/<conta>", methods=["POST"])
def deposit_transaction(conta):
    date_now = datetime.today()
    transaction_date = [date_now.strftime('%Y-%m-%d %H:%M:%S')]
    conn = connection.postgre_sql()
    try:
        sql_saldo = """select * from contas 
                    where conta = '{}' """
        conn.execute(sql_saldo.format(conta))
        data = pd.DataFrame(conn, columns=columns_accounts)

        # Só é possível realizar transação com a conta ativa
        if data['status_conta'][0] != "Ativa":
            error_response = ErrorResponse(
                "Conta desativada", HTTPStatus.BAD_REQUEST)
            return error_response.__handler_response__()

        if data["saldo"][0] < 0:
            saldo_atual = data["saldo"][0] * -1
            balance = request.json["valor_deposito"] - saldo_atual
            if data['limite'][0] < 2000:
                if balance <0:
                    limit = request.json["valor_deposito"] + data['limite'][0]
                else:
                    limit = request.json["valor_deposito"] - \
                        balance + data['limite'][0]
            else:
                balance = balance
                limit = data['limite'][0]
        else:
            balance = data["saldo"][0] + request.json["valor_deposito"]
            limit = data['limite'][0]

        # valida cpf
        if Validator_docbr(request.json["cpf"], 'cpf'):
            sql_transacoes = """
                UPDATE contas SET saldo = '{}', limite = '{}'
                WHERE conta = '{}'
                """.format(
                balance,
                limit,
                conta
            )
            conn.execute(sql_transacoes)
            conn.connection.commit()

            sql_extrato = """
                INSERT INTO transacoes(conta, agencia, cpf, portador, tipo_transacao, data_transacao, valor_deposito, saldo)
                VALUES('{}', '{}', '{}', '{}', '{}', '{}', {}, {})
                """.format(
                data["conta"][0],
                request.json["agencia"],
                request.json["cpf"],
                request.json["portador"],
                "deposito",
                transaction_date[0],
                request.json["valor_deposito"],
                balance
            )
            conn.execute(sql_extrato)
            conn.connection.commit()
            return Response(json.dumps({"mensagem": "transacao efetuada"}))

    except Exception as e:
        error_response = ErrorResponse(
            e.args[0], HTTPStatus.BAD_REQUEST)
        return error_response.__handler_response__()
    error_response = ErrorResponse("Error", HTTPStatus.BAD_REQUEST)
    return error_response.__handler_response__()


@blueprint.app_errorhandler(HTTP_404_NOT_FOUND)
def handle_404_error(_error):
    return make_response(json.dumps({"error": "Not found"}), HTTP_404_NOT_FOUND)


@blueprint.app_errorhandler(HTTP_405_METHOD_NOT_ALLOWED)
def handle_405_error(_error):
    return make_response(json.dumps({"error": "Method not allowed for the requested url"}), HTTP_405_METHOD_NOT_ALLOWED)

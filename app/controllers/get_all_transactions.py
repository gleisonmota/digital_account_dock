import pandas as pd
from flask import Blueprint, Response, make_response
from app.repositories.connection_db import ConnectionDb
from app.templates.http_status_codes import HTTP_404_NOT_FOUND
from app.templates.http_status_codes import HTTP_405_METHOD_NOT_ALLOWED
from app.validators.error_response import ErrorResponse
from http import HTTPStatus
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

blueprint = Blueprint("get_all_transactions", __name__)


columns_transactions = [
    "id",
    "conta",
    "agencia",
    "cpf",
    "portador",
    "tipo_transacao",
    "data_transacao",
    "valor_saque",
    "valor_deposito",
    "saldo"
]


@blueprint.route("/transacoes/<conta>", methods=["GET"])
def get_transactions(conta):
    conn = connection.postgre_sql()
    try:
        sql = """select * from transacoes
                where conta = '{}' """
        conn.execute(sql.format(conta))
        df_data = pd.DataFrame(conn, columns=columns_transactions)
        if not df_data.empty:
            accounts = []
            for index, row in df_data.iterrows():
                account = {
                    "conta": row["conta"],
                    "agencia": row["agencia"],
                    "cpf": row["cpf"],
                    "portador": row["portador"],
                    "tipo_transacao": row["tipo_transacao"],
                    "data_transacao": str(row["data_transacao"]),
                    "valor_saque": row["valor_saque"],
                    "valor_deposito": row["valor_deposito"],
                    "saldo": row["saldo"]
                }
                accounts.append(account)

            return Response(json.dumps(accounts))
        else:
            error_response = ErrorResponse(
            "Não há transacoes", HTTPStatus.BAD_REQUEST)
            return error_response.__handler_response__()

    except Exception as e:
        error_response = ErrorResponse(
        "Error", HTTPStatus.BAD_REQUEST)
        return error_response.__handler_response__()


@blueprint.app_errorhandler(HTTP_404_NOT_FOUND)
def handle_404_error(_error):
    return make_response(json.dumps({"error": "Not found"}), HTTP_404_NOT_FOUND)


@blueprint.app_errorhandler(HTTP_405_METHOD_NOT_ALLOWED)
def handle_405_error(_error):
    return make_response(json.dumps({"error": "Method not allowed for the requested url"}), HTTP_405_METHOD_NOT_ALLOWED)

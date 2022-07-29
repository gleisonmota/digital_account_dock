import pandas as pd
from flask import Blueprint, Response, make_response
from app.repositories.connection_db import ConnectionDb
from app.templates.http_status_codes import HTTP_404_NOT_FOUND
from app.templates.http_status_codes import HTTP_405_METHOD_NOT_ALLOWED
import json
import sys
import os

dirName, ___DUMMY = os.path.split(os.path.abspath(__file__))
sys.path.append(os.path.join(dirName))

config = json.loads(
    open(dirName + "\\..\\templates\\config.json", "r", encoding="utf-8").read())

host = config["db_host"]
dbname = config["db_dbname"]
user = config["db_user"]
psw = config["db_password"]

connection = ConnectionDb(host, dbname, user, psw)

blueprint = Blueprint("delete_account", __name__)

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


@blueprint.route("/contas/<conta>", methods=["DELETE"])
def delete_account(conta):
    conn = connection.postgre_sql()
    try:
        sql = """select * from contas 
                    where conta = '{}' """
        conn.execute(sql.format(conta))
        data = pd.DataFrame(conn, columns=columns_accounts)
        if not data.empty:
            # para manter histórico, mantive um update ao invés de delete
            if data["status_conta"][0] != "Desativada":
                sql = """
                    UPDATE contas SET status_conta = 'Desativada'
                    WHERE conta = '{}';
                """
                conn.execute(sql.format(conta))
                conn.connection.commit()
                return Response(json.dumps({"mensagem": "Conta desativada com sucesso!"}))
            else:
                return Response(json.dumps({"mensagem": "Conta ja desativada"}))

        else:
            return Response(json.dumps({"mensagem": "Conta nao encontrada"}))

    except Exception as e:
        return Response(json.dumps({"mensagem": "Error"}))


@blueprint.app_errorhandler(HTTP_404_NOT_FOUND)
def handle_404_error(_error):
    return make_response(json.dumps({"error": "Not found"}), HTTP_404_NOT_FOUND)


@blueprint.app_errorhandler(HTTP_405_METHOD_NOT_ALLOWED)
def handle_404_error(_error):
    return make_response(json.dumps({"error": "Method not allowed for the requested url"}), HTTP_405_METHOD_NOT_ALLOWED)

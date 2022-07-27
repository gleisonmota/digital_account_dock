import pandas as pd
from flask import Blueprint, Response
from app.repositories.server import ConnectionDb
import json
import sys, os

dirName, ___DUMMY = os.path.split(os.path.abspath(__file__))
sys.path.append(os.path.join(dirName))

config = json.loads(open(dirName + "\\..\\templates\\config.json", "r", encoding="utf-8").read())

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
            if data["status_conta"][0] != "Desativada": #para manter histórico, mantive um update ao invés de delete
                sql="""
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
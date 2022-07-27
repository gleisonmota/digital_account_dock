import pandas as pd
from flask import Blueprint, Response
from app.repositories.server import ConnectionDb
# from app.templates.http_status_codes import HTTP_404_NOT_FOUND
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

blueprint = Blueprint("get_all_accounts", __name__)


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


@blueprint.route("/contas", methods=["GET"])
def get_all_accounts():
    conn = connection.postgre_sql()
    try:
        sql = """select * from contas
                where status_conta != 'desativada' """
        conn.execute(sql)
        df_data = pd.DataFrame(conn, columns=columns_accounts)
        accounts = []
        for index, row in df_data.iterrows():
            account={
                    "conta":row["conta"], 
                    "agencia":row["agencia"], 
                    "cpf":row["cpf"],
                    "portador":row["portador"],
                    "status_conta":row["status_conta"],
                    "saldo":row["saldo"],
                    "limite":row["limite"],
                    "data_abertura_conta":str(row["data_abertura_conta"])
                    }
            accounts.append(account)
        return Response(json.dumps(accounts))

    except Exception as e:
        return Response(json.dumps({"mensagem": "Error"}))

@blueprint.route("/contas/<conta>", methods=["GET"])
def get_account(conta):
    conn = connection.postgre_sql()
    try:
        sql = """select * from contas
                    where conta = '{}'
                    and status_conta != 'Desativada' """
        conn.execute(sql.format(conta))
        df_data = pd.DataFrame(conn, columns=columns_accounts)
        if not df_data.empty:
            for index, row in df_data.iterrows():
                account={
                        "conta":row["conta"], 
                        "agencia":row["agencia"], 
                        "cpf":row["cpf"],
                        "portador":row["portador"],
                        "status_conta":row["status_conta"],
                        "saldo":row["saldo"],
                        "limite":row["limite"],
                        "data_abertura_conta":str(row["data_abertura_conta"])
                        }

            return Response(json.dumps(account))
        else:
            return Response(json.dumps({"mensagem": "Conta nao encontrada"}))

    except Exception as e:
        return Response(json.dumps({"mensagem": "Error"}))


# @blueprint.errorhandler(HTTP_404_NOT_FOUND)
# def handle_404(e):
#     return json.dumps({"error": "Not found"}), HTTP_404_NOT_FOUND
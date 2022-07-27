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
                account={
                        "conta":row["conta"], 
                        "agencia":row["agencia"], 
                        "cpf":row["cpf"],
                        "portador":row["portador"],
                        "tipo_transacao":row["tipo_transacao"],
                        "data_transacao":str(row["data_transacao"]),
                        "valor_saque":row["valor_saque"],
                        "valor_deposito":row["valor_deposito"],
                        "saldo":row["saldo"]
                        }
                accounts.append(account)

            return Response(json.dumps(accounts))
        else:
            return Response(json.dumps({"mensagem": "Nao ha transacoes"}))

    except Exception as e:
        return Response(json.dumps({"mensagem": "Error"}))


# @blueprint.errorhandler(HTTP_404_NOT_FOUND)
# def handle_404(e):
#     return json.dumps({"error": "Not found"}), HTTP_404_NOT_FOUND
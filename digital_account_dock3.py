import pandas as pd
from flask import Flask, Response, request
import psycopg2
import json
import sys, os
from src.constants.http_status_codes import HTTP_404_NOT_FOUND
from datetime import datetime
from src.validators.validator_docbr import Validator_docbr

app = Flask(__name__)

dirName, ___DUMMY = os.path.split(os.path.abspath(__file__))
sys.path.append(os.path.join(dirName))

config = json.loads(open(dirName+"\\src\controllers\\config.json", "r", encoding="utf-8").read())

host = config["db_host"]
dbname = config["db_dbname"]
user = config["db_user"]
psw = config["db_password"]

conn = psycopg2.connect(
                        host=host,
                        dbname= dbname,
                        user=user,
                        password=psw
                        )

connection = conn.cursor()


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


@app.route("/contas", methods=["GET"])
def get_all_accounts():
    connection = conn.cursor()
    try:
        sql = """select * from contas"""
        connection.execute(sql)
        df_data = pd.DataFrame(connection, columns=columns_accounts)
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


@app.route("/contas/<conta>", methods=["GET"])
def get_account(conta):
    connection = conn.cursor()
    try:
        sql = """select * from contas
                    where conta = '{}' """
        connection.execute(sql.format(conta))
        df_data = pd.DataFrame(connection, columns=columns_accounts)
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


@app.route("/transacoes/<conta>", methods=["GET"])
def get_extract(conta):
    connection = conn.cursor()
    try:
        sql = """select * from transacoes
                where conta = '{}' """
        connection.execute(sql.format(conta))
        df_data = pd.DataFrame(connection, columns=columns_transactions)
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



@app.route("/contas", methods=["POST"])
def create_account():
    date_now = datetime.today()
    DATA_TRANSACAO = [date_now.strftime('%Y-%m-%d %H:%M:%S')]
    limite = 2000
    connection = conn.cursor()
    try:
        sql = """select cpf from contas
                where cpf = '{}' """.format(request.json["cpf"])
        connection.execute(sql)
        data = connection.fetchone()
   
        if not data != None: #verifica se já consta o cpf       
            if not request.json["limite"] > limite: #limite máximo de 2.000
                    if Validator_docbr(str(request.json["cpf"]).zfill(11).replace('.0', ''), 'cpf'): #valida cpf 
                        sql="""
                            INSERT INTO contas (agencia, cpf, portador, status_conta, saldo, limite, data_abertura_conta)
                            VALUES ('{}', '{}', '{}', '{}', {}, {}, '{}')""".format(
                                                        request.json["agencia"], 
                                                        request.json["cpf"], 
                                                        request.json["portador"], 
                                                        request.json["status_conta"], 
                                                        request.json["saldo"], 
                                                        request.json["limite"],
                                                        DATA_TRANSACAO[0]
                                                        ) 

                        connection.execute(sql)
                        conn.commit()
                        return Response(json.dumps({"mensagem": "Conta registrada"}))

            else:
                return Response(json.dumps({"mensagem": "Limite nao liberado, maximo de R$ 2000"}))
        else:
            return Response(json.dumps({"mensagem": "CPF ja consta na base de dados"}))

    except Exception as e:
        if e.args[0] == 'CPF inválido.':
            return Response(json.dumps({"mensagem": "CPF invalido"}))
        return Response(json.dumps({"mensagem": "Error"}))



@app.route("/contas/<conta>", methods=["DELETE"])
def delete_account(conta):
    connection = conn.cursor()
    try:
        sql = """select * from contas 
                    where conta = '{}' """
        connection.execute(sql.format(conta))
        data = pd.DataFrame(connection, columns=columns_accounts)
        if not data.empty:
            if data["status_conta"][0] != "Desativada": #para manter histórico, mantive um update ao invés de delete
                sql="""
                    UPDATE contas SET status_conta = 'Desativada'
                    WHERE conta = '{}';
                """
                connection.execute(sql.format(conta))
                conn.commit()
                return Response(json.dumps({"mensagem": "Conta desativada com sucesso!"}))
            else:
                return Response(json.dumps({"mensagem": "Conta ja desativada"}))

        else:
            return Response(json.dumps({"mensagem": "Conta nao encontrada"}))


    except Exception as e:
        return Response(json.dumps({"mensagem": "Error"}))



@app.route("/contas/<conta>", methods=["PUT"])
def transaction(conta):
    date_now = datetime.today()
    DATA_TRANSACAO = [date_now.strftime('%Y-%m-%d %H:%M:%S')]
    limite = 2000
    connection = conn.cursor()
    try:
        sql_saldo = """select * from contas 
                    where conta = '{}' """
        connection.execute(sql_saldo.format(conta))
        data = pd.DataFrame(connection, columns=columns_accounts)
        saldo_total = request.json["deposito"] + data["saldo"][0]
        saldo_total = saldo_total - request.json["saque"]

        if not request.json["status_conta"] != "ativa": #Só é possível realizar transação com a conta ativa
            if not request.json["limite"] > limite: #limite máximo 2.000
                if request.json["tipo_transacao"] in ("deposito", "saque"):
                    if Validator_docbr(str(request.json["cpf"]).zfill(11).replace('.0', ''), 'cpf'): #valida cpf 
                        if request.json["saque"] <= saldo_total: #não deixa a conta negativa
                            sql_transacoes="""
                                UPDATE contas SET agencia = '{}', cpf = '{}', portador = '{}', status_conta = '{}', saldo = {}, limite = {} 
                                WHERE conta = '{}'
                                """.format(
                                            request.json["agencia"], 
                                            request.json["cpf"], 
                                            request.json["portador"], 
                                            request.json["status_conta"], 
                                            saldo_total,
                                            request.json["limite"],
                                            conta
                                            )
                            connection.execute(sql_transacoes)
                            conn.commit()

                            sql_extrato="""
                                INSERT INTO transacoes(conta, agencia, cpf, portador, tipo_transacao, data_transacao, valor_saque, valor_deposito, saldo)
                                VALUES('{}', '{}', '{}', '{}', '{}', '{}', {}, {}, {})
                                """.format(
                                            data["conta"][0], 
                                            request.json["agencia"], 
                                            request.json["cpf"], 
                                            request.json["portador"], 
                                            request.json["tipo_transacao"],
                                            DATA_TRANSACAO[0],
                                            request.json["saque"], 
                                            request.json["deposito"], 
                                            saldo_total,
                                                    )
                            connection.execute(sql_extrato)
                            conn.commit()
                            return Response(json.dumps({"mensagem": "transacao efetuada"}))

                        else:
                            return Response(json.dumps({"mensagem": "saldo insuficiente"}))
                else:
                    return Response(json.dumps({"mensagem": "transcao nao efetuada"}))
            else:
                return Response(json.dumps({"mensagem": "Limite nao liberado, maximo de R$ 2000"}))
        else:
            return Response(json.dumps({"mensagem": "Conta nao ativa"}))


    except Exception as e:
        if e.args[0] == 'CPF inválido.':
            return Response(json.dumps({"mensagem": "CPF invalido"}))
        return Response(json.dumps({"mensagem": "Error"}))


@app.errorhandler(HTTP_404_NOT_FOUND)
def handle_404(e):
    return json.dumps({"error": "Not found"}), HTTP_404_NOT_FOUND


if __name__ == "__main__":
    # app.config.from_object(config["development"])
    app.run(debug=True)
    
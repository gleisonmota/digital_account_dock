from flask import Blueprint, Response, request, make_response
from app.repositories.connection_db import ConnectionDb
from app.templates.http_status_codes import HTTP_404_NOT_FOUND
from app.templates.http_status_codes import HTTP_405_METHOD_NOT_ALLOWED
from app.validators.validator_docbr import Validator_docbr
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

blueprint = Blueprint("create_requisitions", __name__)


@blueprint.route("/contas", methods=["POST"])
def create_account():
    date_now = datetime.today()
    DATA_TRANSACAO = [date_now.strftime('%Y-%m-%d %H:%M:%S')]
    limite = 2000
    conn = connection.postgre_sql()
    try:
        sql = """select cpf from contas
                where cpf = '{}' """.format(request.json["cpf"])
        conn.execute(sql)
        data = conn.fetchone()

        if data != None:  # verifica se já consta o cpf
            return Response(json.dumps({"mensagem": "CPF ja consta na base de dados"}))

        if request.json["limite"] > limite:  # limite máximo de 2.000
            return Response(json.dumps({"mensagem": "Limite nao liberado, maximo de R$ 2000"}))

        if len(request.json["cpf"]) != 11:
            return Response(json.dumps({"mensagem": "cpf com numeros de caracteres incorretos"}))

        # if Validator_docbr().cpf(10)
        # valida cpf
        if Validator_docbr(str(request.json["cpf"]).zfill(11).replace('.0', ''), 'cpf'):
            sql = """
                INSERT INTO contas (agencia, cpf, portador, status_conta, limite, data_abertura_conta)
                VALUES ('{}', '{}', '{}', '{}', {}, '{}')""".format(
                request.json["agencia"],
                request.json["cpf"],
                request.json["portador"],
                request.json["status_conta"],
                request.json["limite"],
                DATA_TRANSACAO[0]
            )
            conn.execute(sql)
            conn.connection.commit()
            return Response(json.dumps({"mensagem": "Conta registrada"}))

    except Exception as e:
        if e.args[0] == 'CPF inválido.':
            return Response(json.dumps({"mensagem": "CPF invalido"}))
        return Response(json.dumps({"mensagem": "Error"}))


@blueprint.app_errorhandler(HTTP_404_NOT_FOUND)
def handle_404_error(_error):
    return make_response(json.dumps({"error": "Not found"}), HTTP_404_NOT_FOUND)


@blueprint.app_errorhandler(HTTP_405_METHOD_NOT_ALLOWED)
def handle_404_error(_error):
    return make_response(json.dumps({"error": "Method not allowed for the requested url"}), HTTP_405_METHOD_NOT_ALLOWED)

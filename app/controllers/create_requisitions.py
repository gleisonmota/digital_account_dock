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

blueprint = Blueprint("create_requisitions", __name__)


@blueprint.route("/contas", methods=["POST"])
def create_account():
    date_now = datetime.today()
    transaction_date = [date_now.strftime('%Y-%m-%d %H:%M:%S')]
    limit = 2000
    conn = connection.postgre_sql()
    try:
        sql = """select cpf from contas
                where cpf = '{}' """.format(request.json["cpf"])
        conn.execute(sql)
        data = conn.fetchone()

        if data != None:  # verifica se já consta o cpf
            error_response = ErrorResponse(
                "CPF ja consta na base de dados", HTTPStatus.BAD_REQUEST)
            return error_response.__handler_response__()

        if request.json["limite"] > limit:  # limite máximo de 2.000
            error_response = ErrorResponse(
                "Limite nao liberado, maximo de R$ 2000", HTTPStatus.BAD_REQUEST)
            return error_response.__handler_response__()

        if Validator_docbr(request.json["cpf"], 'cpf'):
            sql = """
                INSERT INTO contas (agencia, cpf, portador, status_conta, limite, data_abertura_conta)
                VALUES ('{}', '{}', '{}', '{}', {}, '{}')""".format(
                request.json["agencia"],
                request.json["cpf"],
                request.json["portador"],
                request.json["status_conta"],
                request.json["limite"],
                transaction_date[0]
            )
            conn.execute(sql)
            conn.connection.commit()
            return Response(json.dumps({"mensagem": "Conta registrada"}))

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

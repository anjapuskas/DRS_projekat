from queue import Queue

import flask
from flask import Blueprint, jsonify

transaction_blueprint = Blueprint('transaction_blueprint', __name__)

from Engine.main import mysql

@transaction_blueprint.route('/upisTransakcije', methods = ['POST'])
def initTransaction():
    posiljalac = flask.request.json['posiljalac']
    primalac = flask.request.json['primalac']
    kolicina = flask.request.json['kolicina']
    valuta = flask.request.json['valuta']

    cursor = mysql.connection.cursor()
    cursor.execute(''' INSERT INTO transakcije (posiljalac, primalac, kolicina, valuta) VALUES(%s, %s, %s, %s)''', (posiljalac, primalac, kolicina, valuta))
    mysql.connection.commit()
    cursor.close()

    retVal = {'message' : 'Transaction successfully initialized'}, 200
    return retVal

@transaction_blueprint.route('/transakcija', methods = ['GET'])
def getTransakcije():
    content = flask.request.json
    primalac = content['primalac']
    print(primalac)

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM transakcije WHERE primalac = %s", (primalac,))
    transakcija = cursor.fetchall()
    cursor.close()

    return jsonify(transakcija)

@transaction_blueprint.route('/transakcijaPosiljalac', methods = ['GET'])
def getTransakcijeByPosiljalac():
    content = flask.request.json
    primalac = content['primalac']
    posiljalac = content['posiljalac']
    print(primalac)

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM transakcije WHERE primalac = %s AND posiljalac = %s", (primalac, posiljalac))
    transakcija = cursor.fetchall()
    cursor.close()

    return jsonify(transakcija)

@transaction_blueprint.route('/transakcijaId', methods = ['GET'])
def getTransakcijaById():
    content = flask.request.json
    id = content['id']

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM transakcije WHERE id = %s", (id,))
    transakcija = cursor.fetchone()
    cursor.close()

    return jsonify(transakcija)

@transaction_blueprint.route('/izmenaStanjeObradjen', methods=['POST'])
def izmenaStanjeObradjen():
    content = flask.request.json
    id = content['id']

    cursor = mysql.connection.cursor()
    cursor.execute(''' UPDATE transakcije SET stanje = 'OBRADJEN' WHERE id = %s ''', (id,))
    mysql.connection.commit()
    cursor.close()

    povratnaVrednost = {'message' : 'Transkacija je uspesno obradjena'}, 200
    return povratnaVrednost


@transaction_blueprint.route('/izmenaStanjeOdbijen', methods=['POST'])
def IzmjenaStanjeOdbijen():
    content = flask.request.json
    id = content['id']

    cursor = mysql.connection.cursor()
    cursor.execute(''' UPDATE transakcije SET stanje = 'ODBIJEN' WHERE id = %s ''', (id,))
    mysql.connection.commit()
    cursor.close()

    povratnaVrednost = {'message': 'Transkacija je uspesno odbijena'}, 200
    return povratnaVrednost



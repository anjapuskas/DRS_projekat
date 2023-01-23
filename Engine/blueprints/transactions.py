from multiprocessing import Queue

import flask
from flask import Blueprint, jsonify
from .users import *
import threading
from time import sleep

transaction_blueprint = Blueprint('transaction_blueprint', __name__)

from Engine.main import mysql

queue = Queue()

@transaction_blueprint.route('/upisTransakcije', methods = ['POST'])
def initTransaction():
    posiljalac = flask.request.json['posiljalac']
    primalac = flask.request.json['primalac']
    kolicina = flask.request.json['kolicina']
    valuta = flask.request.json['valuta']
    tip = flask.request.json['tip']

    cursor = mysql.connection.cursor()
    cursor.execute(''' INSERT INTO transakcije (posiljalac, primalac, kolicina, stanje, valuta, tip) VALUES(%s, %s, %s, %s, %s, %s)''', (posiljalac, primalac, kolicina, 'OBRADA', valuta, tip))
    mysql.connection.commit()
    cursor.close()

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT max(id) as id FROM transakcije WHERE primalac = %s AND posiljalac = %s", (primalac, posiljalac))
    transakcijaId = cursor.fetchone()
    cursor.close()

    thread = threading.Thread(target=transkacijaNit, args=(transakcijaId,))
    thread.start()

    retVal = {'message' : 'Transaction successfully initialized'}, 200
    return retVal

@transaction_blueprint.route('/transakcija', methods = ['GET'])
def getTransakcije():
    content = flask.request.json
    posiljalac = content['posiljalac']

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM transakcije WHERE posiljalac = %s", (posiljalac,))
    transakcija = cursor.fetchall()
    cursor.close()

    return jsonify(transakcija)

@transaction_blueprint.route('/transakcijaPosiljalac', methods = ['GET'])
def getTransakcijeByPrimalac():
    content = flask.request.json
    primalac = content['primalac']
    posiljalac = content['posiljalac']

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM transakcije WHERE primalac = %s AND posiljalac = %s", (primalac, posiljalac))
    transakcija = cursor.fetchall()
    cursor.close()

    return jsonify(transakcija)

def  getTransakcijaById(id):
    mydb = MySQLdb.connect(host="localhost", user="root", passwd="admin", db="baza_drs")
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM transakcije WHERE id = %s", (id,))
    transakcija = cursor.fetchone()
    cursor.close()

    return transakcija

def getTransakcijaByIdForNit(id):
    mydb = MySQLdb.connect(host="localhost", user="root", passwd="admin", db="baza_drs")
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM transakcije WHERE id = %s", (id,))
    transakcija = cursor.fetchone()
    cursor.close()

    return jsonify(transakcija)

def izmenaStanjeObradjen(id):

    mydb = MySQLdb.connect(host="localhost", user="root", passwd="admin", db="baza_drs")
    cursor = mydb.cursor()
    cursor.execute(''' UPDATE transakcije SET stanje = 'OBRADJEN' WHERE id = %s ''', (id,))
    mydb.commit()
    cursor.close()

    povratnaVrednost = {'message' : 'Transkacija je uspesno obradjena'}, 200
    return povratnaVrednost


def IzmjenaStanjeOdbijen(id):

    mydb = MySQLdb.connect(host="localhost", user="root", passwd="admin", db="baza_drs")
    cursor = mydb.cursor()
    cursor.execute(''' UPDATE transakcije SET stanje = 'ODBIJEN' WHERE id = %s ''', (id,))
    mydb.commit()
    cursor.close()

    povratnaVrednost = {'message': 'Transkacija je uspesno odbijena'}, 200
    return povratnaVrednost

def transkacijaNit(transakcijaId):
    sleep(30)

    queue.put(transakcijaId)

def procesTransakcija(queue: Queue):
    while 1:
        transakcijaId = 0
        try:
            transakcijaId = queue.get()
        except KeyboardInterrupt:
            break

        transakcija = getTransakcijaById(transakcijaId["id"])
        korisnikPosiljalacEmail = transakcija[1]
        korisnikPrimaocEmail = transakcija[2]

        if transakcija[6] == 'BANK':
            valuta = transakcija[5]
            kolicina = transakcija[3]

            mydb = MySQLdb.connect(host="localhost", user="root", passwd="admin", db="baza_drs")
            cursor = mydb.cursor()
            cursor.execute("SELECT * FROM racun WHERE korisnik = %s AND valuta = %s", (korisnikPosiljalacEmail, valuta))
            racunPosiljalac = cursor.fetchone()
            cursor.close()

            mydb = MySQLdb.connect(host="localhost", user="root", passwd="admin", db="baza_drs")
            cursor = mydb.cursor()
            cursor.execute("SELECT * FROM korisnik WHERE email = %s", (korisnikPrimaocEmail,))
            korisnikPrimaoc = cursor.fetchone()
            cursor.close()

            if korisnikPrimaoc is None:
                IzmjenaStanjeOdbijen(transakcijaId["id"])
            elif racunPosiljalac is None:
                IzmjenaStanjeOdbijen(transakcijaId["id"])
            elif int(racunPosiljalac[2]) < int(kolicina):
                IzmjenaStanjeOdbijen(transakcijaId["id"])
            else:

                mydb = MySQLdb.connect(host="localhost", user="root", passwd="admin", db="baza_drs")
                cursor = mydb.cursor()
                cursor.execute("SELECT * FROM racun WHERE korisnik = %s AND valuta = %s", (korisnikPrimaocEmail, valuta))
                racunPrimaoc = cursor.fetchone()
                cursor.close()


                mydb = MySQLdb.connect(host="localhost", user="root", passwd="admin", db="baza_drs")
                cursor = mydb.cursor()
                cursor.execute("UPDATE racun SET iznos = iznos - %s  WHERE korisnik = %s and valuta = %s",
                               (kolicina, korisnikPosiljalacEmail, valuta))
                mydb.commit()
                cursor.close()
#------------------------------------------------

                if racunPrimaoc:
                    mydb = MySQLdb.connect(host="localhost", user="root", passwd="admin", db="baza_drs")
                    cursor = mydb.cursor()
                    cursor.execute("UPDATE racun SET iznos = iznos + %s  WHERE korisnik = %s AND valuta = %s",
                                   (kolicina, korisnikPrimaocEmail, valuta))
                    mydb.commit()
                    cursor.close()
                else:
                    mydb = MySQLdb.connect(host="localhost", user="root", passwd="admin", db="baza_drs")
                    cursor = mydb.cursor()
                    cursor.execute(''' INSERT INTO racun (korisnik, valuta, iznos) VALUES ( %s, %s, %s)''',
                                   (korisnikPrimaocEmail, valuta, kolicina,))
                    mydb.commit()
                    cursor.close()


                izmenaStanjeObradjen(transakcijaId["id"])
        else :
            kolicina = transakcija[3]

            mydb = MySQLdb.connect(host="localhost", user="root", passwd="admin", db="baza_drs")
            cursor = mydb.cursor()
            cursor.execute("SELECT * FROM korisnik WHERE email = %s", (korisnikPrimaocEmail,))
            korisnikPrimaoc = cursor.fetchone()
            cursor.close()

            mydb = MySQLdb.connect(host="localhost", user="root", passwd="admin", db="baza_drs")
            cursor = mydb.cursor()
            cursor.execute("SELECT * FROM korisnik WHERE email = %s", (korisnikPosiljalacEmail,))
            korisnikPosiljalac = cursor.fetchone()
            cursor.close()

            if korisnikPrimaoc is None:
                IzmjenaStanjeOdbijen(transakcijaId["id"])
            elif int(korisnikPosiljalac[10]) < int(kolicina):
                IzmjenaStanjeOdbijen(transakcijaId["id"])
            else:

                mydb = MySQLdb.connect(host="localhost", user="root", passwd="admin", db="baza_drs")
                cursor = mydb.cursor()
                cursor.execute("UPDATE korisnik SET stanjeNaRacunu = stanjeNaRacunu - %s  WHERE email = %s",
                               (kolicina, korisnikPosiljalacEmail,))
                mydb.commit()
                cursor.close()
#------------------------------------------
                mydb = MySQLdb.connect(host="localhost", user="root", passwd="admin", db="baza_drs")
                cursor = mydb.cursor()
                cursor.execute("UPDATE korisnik SET stanjeNaRacunu = stanjeNaRacunu + %s  WHERE email = %s",
                               (kolicina, korisnikPrimaocEmail,))
                mydb.commit()
                cursor.close()

                izmenaStanjeObradjen(transakcijaId["id"])











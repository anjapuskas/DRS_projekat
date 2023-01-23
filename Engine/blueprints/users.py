
from flask import Blueprint, jsonify
import flask
import MySQLdb

user_blueprint = Blueprint('user_blueprint', __name__)

from Engine.main import mysql



@user_blueprint.route('/korisnik', methods=['GET'])
def getKorisik():
    content = flask.request.json
    _email = content['email']
    return getKorisnik(_email)

@user_blueprint.route('/kartica', methods=['GET'])
def getKartica():
    content = flask.request.json
    brojKartice = content['brojKartice']
    print(brojKartice)
    return getKartica(brojKartice)

@user_blueprint.route('/racuni', methods=['GET'])
def getRacuni():
    content = flask.request.json
    email = content['email']
    return getRacuni(email)

@user_blueprint.route('/email', methods=['GET'])
def getEmail():
    content = flask.request.json
    brojKartice = content['brojKartice']

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT email FROM korisnik WHERE brojKartice = %s", (brojKartice,))
    email = cursor.fetchone()
    cursor.close()

    return email

@user_blueprint.route('/registracija', methods=['POST'])
def registracija():

    ime = flask.request.json['ime']
    prezime = flask.request.json['prezime']
    adresa = flask.request.json['adresa']
    grad = flask.request.json['grad']
    drzava = flask.request.json['drzava']
    brojTelefona = flask.request.json['brojTelefona']
    email = flask.request.json['email']
    lozinka = flask.request.json['lozinka']
    verifikovan = flask.request.json['verifikovan']
    stanjeNaRacunu = flask.request.json['stanjeNaRacunu']


    cursor = mysql.connection.cursor()
    cursor.execute(''' INSERT INTO korisnik (ime, prezime, adresa, grad, drzava, brojTelefona, email, lozinka, verifikovan, stanjeNaRacunu) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',(ime, prezime, adresa, grad, drzava, brojTelefona, email, lozinka, verifikovan, stanjeNaRacunu))
    mysql.connection.commit()
    cursor.close()

    povratnaVrednost = {'message' : 'Korisnik je uspesno registrovan'}, 200
    return povratnaVrednost


@user_blueprint.route('/izmenaKorisnika', methods=['POST'])
def izmeniKorisnika():
    ime = flask.request.json['ime']
    prezime = flask.request.json['prezime']
    adresa = flask.request.json['adresa']
    grad = flask.request.json['grad']
    drzava = flask.request.json['drzava']
    brojTelefona = flask.request.json['brojTelefona']
    email = flask.request.json['email']
    lozinka = flask.request.json['lozinka']

    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE korisnik SET ime = %s, prezime = %s, adresa = %s, grad = %s, drzava = %s, brojTelefona = %s, lozinka = %s WHERE email = %s", (ime, prezime, adresa, grad, drzava, brojTelefona, lozinka, email,))
    mysql.connection.commit()
    cursor.close()

    povratnaVrednost = {'message': 'Korisnikov profil je uspesno izmenjen'}, 200
    return povratnaVrednost

@user_blueprint.route('/verifikujKorisnika', methods=['POST'])
def verifikujKorisnika():
    email = flask.request.json['email']

    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE korisnik SET verifikovan = 1 WHERE email = %s", (email,))
    mysql.connection.commit()
    cursor.close()

    povratnaVrednost = {'message': 'Korisnikov profil je uspesno verifikovan'}, 200
    return povratnaVrednost

@user_blueprint.route('/povezivanjeKarticeKorisnik', methods=['POST'])
def povezivanjeKarticeKorisnik():
    ime = flask.request.json['ime']
    brojKartice = flask.request.json['brojKartice']
    datumIsteka = flask.request.json['datumIsteka']
    kod = flask.request.json['kod']
    email = flask.request.json['email']

    cursor = mysql.connection.cursor()
    cursor.execute(''' INSERT INTO kartica (ime, brojKartice, datumIsteka, kod) VALUES ( %s, %s, %s ,%s)''', (ime, brojKartice, datumIsteka, kod,))
    cursor.execute(''' UPDATE korisnik SET brojKartice = %s, verifikovan = 1, stanjeNaRacunu = stanjeNaRacunu - 1 WHERE email = %s''', (brojKartice, email,))
    mysql.connection.commit()
    cursor.close()

    povratnaVrednost = {'message': 'Korisnikova kartica je uspesno povezana'}, 200
    return povratnaVrednost


@user_blueprint.route('/uplataOnline', methods=['POST'])
def uplataOnline():
    kolicina = flask.request.json['kolicina']
    email = flask.request.json['email']

    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE korisnik SET stanjeNaRacunu = stanjeNaRacunu + %s  WHERE email = %s", (kolicina, email,))
    mysql.connection.commit()
    cursor.close()

    povratnaVrednost = {'message': 'Online uplata je uspesno prosla'}, 200
    return povratnaVrednost

def uplataOnline(kolicina, email):

    mydb = MySQLdb.connect(host="localhost", user="root", passwd="admin", db="baza_drs")
    cursor = mydb.cursor()
    cursor.execute("UPDATE korisnik SET stanjeNaRacunu = stanjeNaRacunu + %s  WHERE email = %s", (kolicina, email,))
    mysql.connection.commit()
    cursor.close()

    povratnaVrednost = {'message': 'Online uplata je uspesno prosla'}, 200
    return povratnaVrednost

@user_blueprint.route('/isplataSaRacuna', methods=['POST'])
def isplataSaOnlineRacuna():
    kolicina = int(flask.request.json['kolicina'])
    email = flask.request.json['email']

    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE korisnik SET stanjeNaRacunu = stanjeNaRacunu - %s  WHERE email = %s", (kolicina, email,))
    mysql.connection.commit()
    cursor.close()

    povratnaVrednost = {'message': 'Online isplata je uspesno prosla'}, 200
    return povratnaVrednost

@user_blueprint.route('/uplataBankovniRacun', methods=['POST'])
def uplataBankovniRacun():
    kolicina = flask.request.json['kolicina']
    email = flask.request.json['email']
    valuta = flask.request.json['valuta']

    uplataBankovniRacun(email, kolicina, valuta)

    povratnaVrednost = {'message': 'Uplata na bankovni racun je uspesno prosla'}, 200
    return povratnaVrednost

def uplataBankovniRacun(email, kolicina, valuta):

    mydb = MySQLdb.connect(host="localhost", user="root", passwd="admin", db="baza_drs")
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM racun WHERE korisnik = %s AND valuta = %s", (email, valuta))
    racun = cursor.fetchone()
    cursor.close()

    if racun:
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE racun SET iznos = iznos + %s  WHERE korisnik = %s AND valuta = %s", (kolicina, email, valuta))
        mysql.connection.commit()
        cursor.close()
    else:
        cursor = mysql.connection.cursor()
        cursor.execute(''' INSERT INTO racun (korisnik, valuta, iznos) VALUES ( %s, %s, %s)''',
                       (email, valuta, kolicina,))
        mysql.connection.commit()
        cursor.close()

@user_blueprint.route('/isplataBankovniRacun', methods=['POST'])
def isplataBankovniRacun():
    kolicina = flask.request.json['kolicina']
    email = flask.request.json['email']
    valuta = flask.request.json['valuta']

    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE racun SET iznos = iznos - %s  WHERE korisnik = %s and valuta = %s", (kolicina, email, valuta))
    mysql.connection.commit()
    cursor.close()

    povratnaVrednost = {'message': 'Isplata sa bankovnog racuna je uspesno prosla'}, 200
    return povratnaVrednost

@user_blueprint.route('/uplataNaSopstvenRacun', methods=['POST'])
def uplataNaSopstvenRacun():
    kolicina = flask.request.json['kolicina']
    valuta = flask.request.json['valuta']
    email = flask.request.json['email']

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM racun WHERE korisnik = %s AND valuta = %s", (email, valuta))
    racun = cursor.fetchone()
    cursor.close()

    if racun:

        noviIznos = racun["iznos"] + kolicina
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE racun SET iznos = %s  WHERE korisnik = %s AND valuta = %s", (noviIznos, email, valuta))
        mysql.connection.commit()
        cursor.close()
    else:
        cursor = mysql.connection.cursor()
        cursor.execute(''' INSERT INTO racun (korisnik, valuta, iznos) VALUES ( %s, %s, %s)''',
                       (email, valuta, kolicina,))
        mysql.connection.commit()
        cursor.close()

    povratnaVrednost = {'message': 'Uplata na bankovni racun je uspesno prosla'}, 200
    return povratnaVrednost

def getKorisnik(email: str) -> dict:
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM korisnik WHERE email = %s", (email,))
    korisnik = cursor.fetchone()
    cursor.close()
    if korisnik is None:
        return {}
    else:
        return korisnik

def getKorisnikForNit(email: str) -> dict:
    mydb = MySQLdb.connect(host="localhost", user="root", passwd="admin", db="baza_drs")
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM korisnik WHERE email = %s", (email,))
    korisnik = cursor.fetchone()
    cursor.close()
    return korisnik

def getRacuni(email: str) -> dict:


    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM racun WHERE korisnik = %s", (email,))
    racuni = cursor.fetchall()
    cursor.close()

    return jsonify(racuni)

def getRacunByKorisnikAndValuta(email: str, valuta: str) -> dict:
    mydb = MySQLdb.connect(host="localhost", user="root", passwd="admin", db="baza_drs")
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM racun WHERE korisnik = %s AND valuta = %s", (email,valuta))
    racun = cursor.fetchone()
    cursor.close()

    return racun

def getKartica(brojKartice: str) -> dict:
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM kartica WHERE brojKartice = %s", (brojKartice,))
    kartica = cursor.fetchone()
    cursor.close()
    if kartica is None:
        return {}
    else:
        return kartica

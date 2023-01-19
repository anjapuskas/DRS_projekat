
from flask import Blueprint
import flask

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
    stanjeUBanci = flask.request.json['stanjeUBanci']


    cursor = mysql.connection.cursor()
    cursor.execute(''' INSERT INTO korisnik (ime, prezime, adresa, grad, drzava, brojTelefona, email, lozinka, verifikovan, stanjeNaRacunu, stanjeUBanci) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',(ime, prezime, adresa, grad, drzava, brojTelefona, email, lozinka, verifikovan, stanjeNaRacunu, stanjeUBanci))
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

@user_blueprint.route('/izmeniStanja', methods=['POST'])
def izmeniStanja():
    stanjeNaRacunu = flask.request.json['stanjeNaRacunu']
    stanjeUBanci = flask.request.json['stanjeUBanci']
    email = flask.request.json['email']
    print(stanjeNaRacunu)
    print(stanjeUBanci)

    cursor = mysql.connection.cursor()
    cursor.execute(''' UPDATE korisnik SET stanjeNaRacunu = %s, stanjeUBanci = %s WHERE email = %s ''', (stanjeNaRacunu,stanjeUBanci,email,))
    mysql.connection.commit()
    cursor.close()

    povratnaVrednost = {'message': 'Korisnikovo stanje je uspesno izmenjeno'}, 200
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

@user_blueprint.route('/isplataSaRacuna', methods=['POST'])
def isplataSaRacuna():
    kolicina = flask.request.json['kolicina']
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

    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE korisnik SET stanjeUBanci = stanjeUBanci + %s  WHERE email = %s", (kolicina, email,))
    mysql.connection.commit()
    cursor.close()

    povratnaVrednost = {'message': 'Uplata na bankovni racun je uspesno prosla'}, 200
    return povratnaVrednost

@user_blueprint.route('/isplataBankovniRacun', methods=['POST'])
def isplataBankovniRacun():
    kolicina = flask.request.json['kolicina']
    email = flask.request.json['email']

    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE korisnik SET stanjeUBanci = stanjeUBanci - %s  WHERE email = %s", (kolicina, email,))
    mysql.connection.commit()
    cursor.close()

    povratnaVrednost = {'message': 'Isplata sa bankovnog racuna je uspesno prosla'}, 200
    return povratnaVrednost



def getKorisnik(email: str) -> dict:
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM korisnik WHERE email = %s", (email,))
    korisnik = cursor.fetchone()
    cursor.close()
    return korisnik

def getKartica(brojKartice: str) -> dict:
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM kartica WHERE brojKartice = %s", (brojKartice,))
    kartica = cursor.fetchone()
    cursor.close()
    return kartica

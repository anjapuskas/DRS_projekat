import json

import requests
from flask import Flask, request, session, render_template
from flask_mysqldb import MySQL

app = Flask(__name__)

app.secret_key = "123"

@app.route("/")
def start():
    return render_template("Login.html")
@app.route('/Logout')
def logout():
    session.pop("korisnik", None)
    return render_template("Login.html")

@app.route("/PrikaziRegistraciju", methods=['POST', 'GET'])
def prikaziRegistraciju():
     return render_template('Registracija.html')

@app.route("/PrikaziDepozit", methods=['POST', 'GET'])
def prikaziDepozit():
    session["mogucaUplata"] = 1
    return render_template('Depozit.html')

@app.route("/PrikaziOnlineRacun", methods=['POST', 'GET'])
def prikaziOnlineRacun():
    session["mogucaUplata"] = 1
    return render_template('OnlineRacun.html')

@app.route("/PrikaziBankovniRacun", methods=['POST', 'GET'])
def prikaziBankovniRacun():
    session["mogucaUplata"] = 1
    return render_template('BankovniRacun.html')


@app.route("/PrikaziIzmenuProfila", methods=['POST', 'GET'])
def prikaziIzmenuProfila():
    email = session["email"]
    korisnik = getKorisnik(email)
    return render_template('IzmeniProfil.html', korisnik = korisnik)


#PrikaziPregledTransakcija
@app.route("/PrikaziPregledTransakcija", methods=['GET', 'POST'])
def prikaziPregledTransakcija():
    email = session["email"]
    korisnik = getKorisnik(email)
    transakcije = getTransakciju(email)
    return render_template('PregledTransakcija.html',transakcije = transakcije, korisnik = korisnik)


@app.route("/PrikaziIndex", methods=['GET', 'POST'])
def prikaziIndex():
    email = session["email"]
    korisnik = getKorisnik(email)
    return render_template('Index.html', korisnik = korisnik)
#################################################################################################################


@app.route("/Registracija", methods=['GET', 'POST'])
def registracija():

    ime = request.form['inputIme']
    prezime = request.form['inputPrezime']
    adresa = request.form['inputAdresa']
    grad = request.form['inputGrad']
    drzava = request.form['inputDrzava']
    brojTelefona = request.form['inputBrojTelefona']
    email = request.form['inputEmail']
    lozinka = request.form['inputLozinka']
    verifikovan = 0
    stanjeNaRacunu = 2
    stanjeUBanci = 100000

    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    body = json.dumps(
        {'ime': ime, 'prezime': prezime, 'adresa': adresa, 'grad': grad, 'drzava': drzava,
         'brojTelefona': brojTelefona, 'email': email, 'lozinka': lozinka, 'verifikovan': verifikovan, 'stanjeNaRacunu': stanjeNaRacunu,
         'stanjeUBanci': stanjeUBanci})
    req = requests.post("http://127.0.0.1:8000/api/registracija", data=body, headers=headers)

    response = (req.json())
    _message = response['message']
    _code = req.status_code
    return render_template("Login.html")


@app.route("/IzmeniProfil", methods=['GET', 'POST'])
def izmeniProfil():

    ime = request.form['inputIme']
    prezime = request.form['inputPrezime']
    adresa = request.form['inputAdresa']
    grad = request.form['inputGrad']
    drzava = request.form['inputDrzava']
    brojTelefona = request.form['inputBrojTelefona']
    lozinka = request.form['inputLozinka']

    email = session["email"]

    korisnik = getKorisnik(email)

    izmeniKorisnika(email, ime, prezime, adresa, grad, drzava, brojTelefona, lozinka)
    korisnik1 = getKorisnik(email)
    poruka = "Uspesna modifikacija"
    return render_template("Index.html", errormsg = poruka, korisnik = korisnik1)


@app.route("/Login", methods=['GET', 'POST'])
def login():
    email = request.form['inputEmail']
    lozinka = request.form['inputLozinka']

    korisnik = getKorisnik(email)

    if korisnik != None and korisnik["email"] == email and korisnik["lozinka"] == lozinka:
        #poruka = "Uspjesno logovanje!"
        session["email"] = email
        if korisnik["verifikovan"] == 0:
            return render_template("Verifikacija.html")
        else:
            return render_template("Index.html",korisnik = korisnik)
    else:
        poruka = "Nespravan email ili lozinka!"
    return render_template("Login.html", errormsg=poruka)


@app.route("/Verifikacija", methods=['GET', 'POST'])
def verifikacija():
    ime = request.form['inputIme']
    brojKartice = request.form['inputBrojKartice']
    mjesec = request.form['inputMjesec']
    godina = request.form['inputGodina']
    kod = request.form['inputKod']

    datumIsteka = mjesec + '/' + godina


    email = session["email"]

    korisnik = getKorisnik(email)
    stanjeNaRacunu = korisnik["stanjeNaRacunu"]

    if korisnik != None and korisnik["ime"] == ime and len(kod) == 3 and len(brojKartice) == 16:
        #poruka = "Uspesno logovanje!"
        verifikujKorisnika(email)
        povezivanjeKarticeiKorisnika(email, ime, brojKartice, datumIsteka, kod, stanjeNaRacunu)
        korisnik1 = getKorisnik(email)

        return render_template("Index.html", korisnik = korisnik1)
    else:
        poruka = "Neuspesno logovanje"
        return render_template("Verifikacija.html", errormsg=poruka)

@app.route("/Depozit", methods=['GET', 'POST'])
def uplataNaRacun():
    kod = request.form['inputKod']
    suma = request.form['inputSuma']

    email = session["email"]
    korisnik = getKorisnik(email)
    kartica = getKartica(korisnik["brojKartice"])

    if session["mogucaUplata"] == 1:

        if float(suma) <= 0:
            poruka = "Uplata na racun mora biti  veca od 0"
            return render_template("/Depozit.html", errormsg=poruka)

        if kod != kartica["kod"]:
            poruka = "Pogresan kod"
            return render_template("/Depozit.html", errormsg=poruka)



        stanjeNaRacunu = korisnik["stanjeNaRacunu"]
        stanjeUBanci = korisnik["stanjeUBanci"]


        if stanjeUBanci >= int(suma):
            stanjeNaRacunu += int(suma)
            stanjeUBanci -= int(suma)

            IzmeniStanja(email, stanjeNaRacunu, stanjeUBanci)
           # updateKorisnika(email, korisnik["ime"], korisnik["prezime"], korisnik["adresa"], korisnik["grad"], korisnik["drzava"], korisnik["brojTelefona"], korisnik["lozinka"], stanjeNaRacunu, stanjeUBanci)
            korisnik1 = getKorisnik(email)
            session["mogucaUplata"] = 0
            return  render_template("/Index.html", korisnik = korisnik1)
        else:
            poruka = "Nemate dovoljno novca na bankovnom racunu"
            return render_template("/Depozit.html", errormsg=poruka)
    else:
        return render_template("/Index.html", korisnik=korisnik)



@app.route("/OnlineRacun", methods=['GET', 'POST'])
def onlineRacun():
    email = request.form['inputEmail']
    kolicina = request.form['inputKolicina']

    korisnik = getKorisnik(email) #onaj kome salje
    email1 = session["email"]
    korisnik1 = getKorisnik(email1)  #onaj ko salje

    if session["mogucaUplata"] == 1:
        if float(kolicina) <= 0:
            poruka = "Morate uplatiti sumu vecu od 0."
            return render_template("OnlineRacun.html", errormsg=poruka)

        if korisnik1["stanjeNaRacunu"] < 0:
            poruka = "Nemate dovoljno novca na racunu."
            return render_template("OnlineRacun.html", errormsg=poruka)

        if korisnik == None:
            poruka = "Korisnik  nema registrovan nalog."
            return render_template("OnlineRacun.html", errormsg=poruka)

        if float(kolicina) > korisnik1["stanjeNaRacunu"]:
            poruka = "Nema dovoljno novca"
            return render_template("OnlineRacun.html", errormsg=poruka)


        #USPJESNO  treba nam upit da se upisu pare u bazu

        uplataNaOnline(email, kolicina)
        isplataSaRacunaPosiljaoca(email1, kolicina)

        korisnik2 = getKorisnik(email1)

        upisTransakcije(email1, email, kolicina)

        session["mogucaUplata"] = 0
        return render_template("Index.html", korisnik=korisnik2)
    else:
        return render_template("Index.html", korisnik=korisnik1)


@app.route("/BankovniRacun", methods=['GET', 'POST'])
def BankovniRacun():
    brojKartice = request.form['inputBrojKartice']
    kolicina = request.form['inputKolicina']

    # PRIMALAC
    kartica = getKartica(brojKartice) #onaj kome salje
    email2 = getEmail(brojKartice)

    emailPrimaoca = email2["email"]


    #POSILJALAC KORISNIK1
    email1 = session["email"]
    korisnik1 = getKorisnik(email1)
    karitca1 = korisnik1["brojKartice"]  #onaj ko salje

    if session["mogucaUplata"] == 1:

        if float(kolicina) <= 0:
            poruka = "Morate uplatiti sumu vecu od 0."
            return render_template("BankovniRacun.html", errormsg=poruka)

        if korisnik1["stanjeUBanci"] < 0:
            poruka = "Nemate dovoljno novca u banci."
            return render_template("BankovniRacun.html", errormsg=poruka)

        if len(brojKartice) != 16:
            poruka = "Niste unijeli dobar format broja racuna."
            return render_template("BankovniRacun.html", errormsg=poruka)

        if brojKartice  != kartica["brojKartice"]:
            poruka = "Ne postoji registrovan korisnik sa tim brojem racuna"
            return render_template("BankovniRacun.html", errormsg=poruka)


        #USPJESNO  treba nam upit da se upisu pare u bazu
        uplataNaBankovniRacun(emailPrimaoca, kolicina)
        isplataSaBankovnogRacunaPosiljaoca(email1, kolicina)
        korisnik2 = getKorisnik(email1)

        upisTransakcije(email1, emailPrimaoca, kolicina)

        session["mogucaUplata"] = 0
        return render_template("Index.html", korisnik=korisnik2)
    else:
        return render_template("Index.html", korisnik=korisnik1)


@app.route("/PrikaziPregledTransakcija", methods=['GET', 'POST'])
def pregledTransakcija():

    primalac = session["email"]
    transakcije = getTransakciju(primalac)

    return render_template("PregledTransakcija.html", transakcije=transakcije)




@app.route("/PrihvatiTransakciju", methods=['GET', 'POST'])
def prihvatiTransakciju():

    email = session["email"]
    korisnik = getKorisnik(email)

    transakcije = getTransakciju(email)
    idd = transakcije["id"]
    id1 = '000000000' + str(idd)
    print(id1)


    IzmjenaStanjeObradjen(id1)
    return render_template("PregledTransakcija.html", transakcije=transakcije, korisnik = korisnik)

@app.route("/OdbijTransakciju", methods=['GET', 'POST'])
def odbijTransakciju():

    email = session["email"]
    transakcije = getTransakciju(email)
    korisnik = getKorisnik(email)
    id = transakcije["id"]
    id1 = '00000000' + str(id)
    print(id1)
    IzmjenaStanjeOdbijen(id1)
    return render_template("PregledTransakcija.html", transakcije=transakcije, korisnik = korisnik)




########################################################################################################################

def getKorisnik(email: str) -> dict:

    headers = {'Content-type' : 'application/json', 'Accept': 'text/plain'}
    body = json.dumps({'email': email})
    req = requests.get("http://127.0.0.1:8000/api/korisnik", data = body, headers = headers)
    return req.json()



def getKartica(brojKartice: str) -> dict:

    headers = {'Content-type' : 'application/json', 'Accept': 'text/plain'}
    body = json.dumps({'brojKartice': brojKartice})
    req = requests.get("http://127.0.0.1:8000/api/kartica", data = body, headers = headers)
    return req.json()

def getTransakciju(primalac: str) -> list:
    headers = {'Content-type' : 'application/json', 'Accept': 'text/plain'}
    body = json.dumps({'primalac': primalac})
    req = requests.get("http://127.0.0.1:8000/api/transakcija", data = body, headers = headers)
    return req.json()



############


def getEmail(brojKartice: str) -> dict:
    headers = {'Content-type' : 'application/json', 'Accept': 'text/plain'}
    body = json.dumps({'brojKartice': brojKartice})
    req = requests.get("http://127.0.0.1:8000/api/email", data = body, headers = headers)
    return req.json()


def povezivanjeKarticeiKorisnika(email : str, ime : str, brojKartice : str, datumIsteka : str, kod : str, stanjeNaRacunu):

    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    body = json.dumps(
        {'email': email, 'ime': ime, 'brojKartice': brojKartice, 'datumIsteka': datumIsteka, 'kod': kod,
         'stanjeNaRacunu': stanjeNaRacunu})
    req = requests.post("http://127.0.0.1:8000/api/povezivanjeKarticeKorisnik", data=body, headers=headers)
    return req

def IzmeniStanja(email: str, stanjeNaRacunu : int, stanjeUBanci : int):

    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    body = json.dumps(
        {'email': email, 'stanjeNaRacunu': stanjeNaRacunu, 'stanjeUBanci': stanjeUBanci})
    req = requests.post("http://127.0.0.1:8000/api/izmeniStanja", data=body, headers=headers)
    return req

def upisTransakcije( posiljalac, primalac, kolicina):

    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    body = json.dumps(
        {'posiljalac': posiljalac, 'primalac': primalac, 'kolicina': kolicina})
    req = requests.post("http://127.0.0.1:8000/api/upisTransakcije", data=body, headers=headers)
    return req

def verifikujKorisnika(email):

    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    body = json.dumps({'email': email})
    req = requests.post("http://127.0.0.1:8000/api/verifikujKorisnika", data=body, headers=headers)
    return req


def izmeniKorisnika(email, ime, prezime, adresa, grad, drzava, brojTelefona, lozinka):
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    body = json.dumps(
        {'email': email, 'ime': ime, 'prezime': prezime, 'grad': grad, 'adresa': adresa, 'drzava': drzava,
         'brojTelefona': brojTelefona, 'lozinka': lozinka})
    req = requests.post("http://127.0.0.1:8000/api/izmenaKorisnika", data=body, headers=headers)
    return req

def uplataNaOnline(email, kolicina):
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    body = json.dumps(
        {'email': email, 'kolicina': kolicina})
    req = requests.post("http://127.0.0.1:8000/api/uplataOnline", data=body, headers=headers)
    return req

def isplataSaRacunaPosiljaoca(email, kolicina):
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    body = json.dumps(
        {'email': email, 'kolicina': kolicina})
    req = requests.post("http://127.0.0.1:8000/api/isplataSaRacuna", data=body, headers=headers)
    return req

def uplataNaBankovniRacun(email, kolicina):
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    body = json.dumps(
        {'email': email, 'kolicina': kolicina})
    req = requests.post("http://127.0.0.1:8000/api/uplataBankovniRacun", data=body, headers=headers)
    return req

def isplataSaBankovnogRacunaPosiljaoca(email, kolicina):
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    body = json.dumps(
        {'email': email, 'kolicina': kolicina})
    req = requests.post("http://127.0.0.1:8000/api/isplataBankovniRacun", data=body, headers=headers)
    return req


def  IzmjenaStanjeObradjen(id):
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    body = json.dumps(
        {'id': id})
    req = requests.post("http://127.0.0.1:8000/api/IzmjenaStanjeObradjen", data=body, headers=headers)
    return req

def  IzmjenaStanjeOdbijen(id):
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    body = json.dumps(
        {'id': id})
    req = requests.post("http://127.0.0.1:8000/api/IzmjenaStanjeOdbijen", data=body, headers=headers)
    return req





if __name__ == '__main__':
    app.run(debug=True)
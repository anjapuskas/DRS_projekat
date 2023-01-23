import json

import requests
from flask import Flask, request, session, render_template
from flask_mysqldb import MySQL
import datetime

app = Flask(__name__)

app.secret_key = "123"

@app.route("/")
def start():
    return render_template("Login.html")
@app.route('/Logout')
def logout():
    session["korisnik"] = None
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
    valute = getValuteList()
    return render_template('BankovniRacun.html', valute = valute)

@app.route("/PrikaziMenjacnicu", methods=['POST', 'GET'])
def prikaziMenjacnicu():
    session["mogucaUplata"] = 1
    valute = getValuteList()
    return render_template('Menjacnica.html', valute = valute)


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
    transakcije = getTransakcije(email)
    return render_template('PregledTransakcija.html',transakcije = transakcije, korisnik = korisnik)


@app.route("/PrikaziIndex", methods=['GET', 'POST'])
def prikaziIndex():
    email = session["email"]
    korisnik = getKorisnik(email)
    racuni = getRacuni(email)
    return render_template('Index.html', korisnik = korisnik, racuni = racuni)
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

    if getKorisnik(email) == {}:

        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        body = json.dumps(
            {'ime': ime, 'prezime': prezime, 'adresa': adresa, 'grad': grad, 'drzava': drzava,
             'brojTelefona': brojTelefona, 'email': email, 'lozinka': lozinka, 'verifikovan': verifikovan, 'stanjeNaRacunu': stanjeNaRacunu})
        req = requests.post("http://127.0.0.1:8000/api/registracija", data=body, headers=headers)

        uplataNaSopstvenRacun(email, 100000, 'RSD')

        response = (req.json())
        _message = response['message']
        _code = req.status_code
        return render_template("Login.html")
    else:
        poruka = "Korisnik sa unesenim emailom vec postoji"
        return render_template("Registracija.html", errormsg=poruka)


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
    racuni = getRacuni(email)

    izmeniKorisnika(email, ime, prezime, adresa, grad, drzava, brojTelefona, lozinka)
    korisnik1 = getKorisnik(email)
    poruka = "Uspesna modifikacija"
    return render_template("Index.html", errormsg = poruka, korisnik = korisnik1, racuni = racuni)


@app.route("/Login", methods=['GET', 'POST'])
def login():
    email = request.form['inputEmail']
    lozinka = request.form['inputLozinka']

    korisnik = getKorisnik(email)
    racuni = getRacuni(email)

    if korisnik != None and korisnik != {} and korisnik["email"] == email and korisnik["lozinka"] == lozinka:
        #poruka = "Uspjesno logovanje!"
        session["email"] = email
        if korisnik["verifikovan"] == 0:
            return render_template("Verifikacija.html")
        else:
            return render_template("Index.html",korisnik = korisnik, racuni = racuni)
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

    today = datetime.date.today()

    if int(godina) < today.year | (int(godina) == today.year & int(mjesec) < today.month):
        poruka = "Godina i mesec kartice moraju biti nakon danasnjeg dana"
        return render_template("Verifikacija.html", errormsg=poruka)

    if getKartica(brojKartice) != {}:
        poruka = "Broj kartice vec postoji"
        return render_template("Verifikacija.html", errormsg=poruka)


    datumIsteka = mjesec + '/' + godina


    email = session["email"]

    korisnik = getKorisnik(email)
    racuni = getRacuni(email)
    stanjeNaRacunu = korisnik["stanjeNaRacunu"]

    if korisnik != None and korisnik["ime"] == ime and len(kod) == 3 and len(brojKartice) == 16:
        #poruka = "Uspesno logovanje!"
        verifikujKorisnika(email)
        povezivanjeKarticeiKorisnika(email, ime, brojKartice, datumIsteka, kod, stanjeNaRacunu)
        korisnik1 = getKorisnik(email)

        return render_template("Index.html", korisnik = korisnik1, racuni = racuni)
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
    racuni = getRacuni(email)

    if session["mogucaUplata"] == 1:

        if float(suma) <= 0:
            poruka = "Uplata na racun mora biti  veca od 0"
            return render_template("/Depozit.html", errormsg=poruka)

        if kartica == {}:
            poruka = "Kartica ne postoji"
            return render_template("/Depozit.html", errormsg=poruka)

        if kod != kartica["kod"]:
            poruka = "Pogresan kod"
            return render_template("/Depozit.html", errormsg=poruka)

        racuni = getRacuni(email)
        stanjeUBanci = 0


        for racun in racuni:
            if 'RSD' == racun["valuta"]:
                stanjeUBanci = racun["iznos"]
                break

        stanjeNaRacunu = korisnik["stanjeNaRacunu"]


        if stanjeUBanci >= int(suma):
            stanjeNaRacunu += int(suma)

            uplataNaOnline(email, suma)
            isplataSaBankovnogRacunaPosiljaoca(email, suma, 'RSD')

            korisnik1 = getKorisnik(email)
            session["mogucaUplata"] = 0
            racuni = getRacuni(email)
            return  render_template("/Index.html", korisnik = korisnik1, racuni = racuni)
        else:
            poruka = "Nemate dovoljno novca na bankovnom racunu"
            return render_template("/Depozit.html", errormsg=poruka)
    else:
        return render_template("/Index.html", korisnik=korisnik, racuni = racuni)



@app.route("/OnlineRacun", methods=['GET', 'POST'])
def onlineRacun():
    email = request.form['inputEmail']
    kolicina = request.form['inputKolicina']

    korisnik = getKorisnik(email) #onaj kome salje
    email1 = session["email"]
    korisnik1 = getKorisnik(email1)  #onaj ko salje
    racuni = getRacuni(email1)

    if session["mogucaUplata"] == 1:
        if float(kolicina) <= 0:
            poruka = "Morate uplatiti sumu vecu od 0."
            return render_template("OnlineRacun.html", errormsg=poruka)
        if email == email1:
            poruka = "Korisnik ne moze poslati sam sebi novac."
            return render_template("OnlineRacun.html", errormsg=poruka)
        #if korisnik == {}:
            #poruka = "Ne postoji korisnik kome se uplacuje novac."
            #return render_template("OnlineRacun.html", errormsg=poruka)



        #USPJESNO  treba nam upit da se upisu pare u bazu

        korisnik2 = getKorisnik(email1)

        upisTransakcije(email1, email, kolicina, 'RSD', 'NET')

        session["mogucaUplata"] = 0
        racuni = getRacuni(email1)
        return render_template("Index.html", korisnik=korisnik2, racuni = racuni)
    else:
        return render_template("Index.html", korisnik=korisnik1, racuni = racuni)


@app.route("/BankovniRacun", methods=['GET', 'POST'])
def BankovniRacun():
    brojKartice = request.form['inputBrojKartice']
    kolicina = request.form['inputKolicina']
    valuta = request.form['inputValuta']

    # PRIMALAC
    kartica = getKartica(brojKartice) #onaj kome salje
    if kartica == {}:
        poruka = "Kartica ne postoji"
        return render_template("/BankovniRacun.html", errormsg=poruka)
    email2 = getEmail(brojKartice)

    emailPrimaoca = email2["email"]


    #POSILJALAC KORISNIK1
    email1 = session["email"]
    korisnik1 = getKorisnik(email1)
    karitca1 = korisnik1["brojKartice"]  #onaj ko salje
    racuni = getRacuni(email1)
    stanjeUBanci = 0

    postoji = 0

    for racun in racuni:
        if valuta == racun["valuta"]:
            postoji = 1
            stanjeUBanci = racun["iznos"]
            break

    if session["mogucaUplata"] == 1:


        if kartica == {}:
            poruka = "Kartica ne postoji"
            return render_template("/BankovniRacun.html", errormsg=poruka)
        if float(kolicina) <= 0:
            poruka = "Morate uplatiti sumu vecu od 0."
            return render_template("BankovniRacun.html", errormsg=poruka)

        if len(brojKartice) != 16:
            poruka = "Niste unijeli dobar format broja racuna."
            return render_template("BankovniRacun.html", errormsg=poruka)

        if brojKartice  != kartica["brojKartice"]:
            poruka = "Ne postoji registrovan korisnik sa tim brojem racuna"
            return render_template("BankovniRacun.html", errormsg=poruka)


        #USPJESNO  treba nam upit da se upisu pare u bazu

        korisnik2 = getKorisnik(email1)

        upisTransakcije(email1, emailPrimaoca, kolicina, valuta, 'BANK')

        session["mogucaUplata"] = 0
        racuni = getRacuni(email1)
        return render_template("Index.html", korisnik=korisnik2, racuni = racuni)
    else:
        return render_template("Index.html", korisnik=korisnik1, racuni = racuni)


@app.route("/ZameniNovac", methods=['GET', 'POST'])
def zameniNovac():
    valuta = request.form['inputValuta']
    kolicina = float(request.form['inputKolicina'])
    kurs = float(getValutaVrednost(valuta))

    email = session["email"]
    korisnik = getKorisnik(email)
    racuni = getRacuni(email)
    stanjeUBanci = 0

    for racun in racuni:
        if valuta == racun["valuta"]:
            postoji = 1
            stanjeUBanci = racun["iznos"]
            break

    if session["mogucaUplata"] == 1:

        if float(kolicina) <= 0:
            poruka = "Morate uplatiti sumu vecu od 0."
            return render_template("Menjacnica.html", errormsg=poruka)

        if korisnik["stanjeNaRacunu"] < kolicina*kurs:
            poruka = "Nemate dovoljno novca na racunu."
            return render_template("Menjacnica.html", errormsg=poruka)


        uplataNaBankovniRacun(email, kolicina, valuta)
        isplataSaRacunaPosiljaoca(email, kolicina*kurs)

        racuni = getRacuni(email)
        korisnik = getKorisnik(email)
        session["mogucaUplata"] = 0
        return render_template("Index.html", korisnik=korisnik, racuni = racuni)
    else:
        return render_template("Index.html", korisnik=korisnik, racuni=racuni)


@app.route("/PrikaziPregledTransakcija", methods=['GET', 'POST'])
def pregledTransakcija():

    primalac = session["email"]
    transakcije = getTransakcije(primalac)

    return render_template("PregledTransakcija.html", transakcije=transakcije)

@app.route("/FilterTransakcije", methods=['GET', 'POST'])
def FilterTransakcije():

    emailPosiljalac = session["email"]
    emailPrimalac = request.form['inputEmail']
    transakcije = getTransakcijeByPrimalac(emailPrimalac, emailPosiljalac)

    return render_template("PregledTransakcija.html", transakcije=transakcije)

@app.route("/SortirajTransakcije", methods=['GET', 'POST'])
def SortirajTransakcije():

    emailPosiljalac = session["email"]
    sortType = str(request.form['sortType']).split("_")
    transakcije = getTransakcije(emailPosiljalac)

    reverse = sortType[1] == "desc"

    if(sortType[0] == 'primalac'):
        transakcije.sort(key=lambda x: x["primalac"], reverse=reverse)
    if (sortType[0] == 'kolicina'):
        transakcije.sort(key=lambda x: int(x["kolicina"]), reverse=reverse)
    if (sortType[0] == 'stanje'):
        transakcije.sort(key=lambda x: x["stanje"], reverse=reverse)

    return render_template("PregledTransakcija.html", transakcije=transakcije)

@app.route("/PrikaziPregledValuta", methods=['GET', 'POST'])
def PrikaziPregledValuta():
    valute = getValuteList()

    return render_template("PregledValuta.html", valute=valute)


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

def getTransakcije(posiljalac: str) -> list:
    headers = {'Content-type' : 'application/json', 'Accept': 'text/plain'}
    body = json.dumps({'posiljalac': posiljalac})
    req = requests.get("http://127.0.0.1:8000/api/transakcija", data = body, headers = headers)
    return req.json()

def getRacuni(email: str) -> dict:

    headers = {'Content-type' : 'application/json', 'Accept': 'text/plain'}
    body = json.dumps({'email': email})
    req = requests.get("http://127.0.0.1:8000/api/racuni", data = body, headers = headers)
    return req.json()

def getTransakcijeByPrimalac(primalac, posiljalac: str) -> list:
    headers = {'Content-type' : 'application/json', 'Accept': 'text/plain'}
    body = json.dumps({'primalac': primalac, 'posiljalac': posiljalac})
    req = requests.get("http://127.0.0.1:8000/api/transakcijaPosiljalac", data = body, headers = headers)
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

def upisTransakcije( posiljalac, primalac, kolicina, valuta, tip):

    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    body = json.dumps(
        {'posiljalac': posiljalac, 'primalac': primalac, 'kolicina': kolicina, 'valuta': valuta, 'tip': tip})
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

def uplataNaBankovniRacun(email, kolicina, valuta):
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    body = json.dumps(
        {'email': email, 'kolicina': kolicina, 'valuta': valuta})
    req = requests.post("http://127.0.0.1:8000/api/uplataBankovniRacun", data=body, headers=headers)
    return req

def isplataSaBankovnogRacunaPosiljaoca(email, kolicina, valuta):
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    body = json.dumps(
        {'email': email, 'kolicina': kolicina, 'valuta': valuta})
    req = requests.post("http://127.0.0.1:8000/api/isplataBankovniRacun", data=body, headers=headers)
    return req

def uplataNaSopstvenRacun(email, kolicina, valuta):
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    body = json.dumps(
        {'email': email, 'kolicina': kolicina, 'valuta': valuta})
    req = requests.post("http://127.0.0.1:8000/api/uplataNaSopstvenRacun", data=body, headers=headers)
    return req

def getValuteList():
    headers = {'apikey': 'Qv3iJFQzumlmBR4RQyfIa7W0csfrJp7v'}
    req = requests.get(
        "https://api.fastforex.io/fetch-all?from=RSD&api_key=a529e6583f-f34933dc88-royn1h", headers=headers)
    content = (req.json())['results']
    valute = []
    # Converts every other currency in base currecy value
    for key, value in content.items():
        if(value != 0):
            valuta = {}
            valuta["valuta"] = key
            valuta["vrednost"] = 1 / value
            valute.append(valuta)
    return valute

def getValutaVrednost(valuta):
    valute = getValuteList()
    for v in valute:
        if valuta == v["valuta"]:
            return v["vrednost"]

    return 0

if __name__ == '__main__':
    app.run(debug=True)
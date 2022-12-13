from flask import Flask, request, session, render_template
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'admin'
app.config['MYSQL_DB'] = 'baza_drs'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'  # da nam baza vraca dictionary sa header-ima iz baze podataka

mysql = MySQL(app)
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
     return render_template('Depozit.html')


@app.route("/PrikaziIzmenuProfila", methods=['POST', 'GET'])
def prikaziIzmenuProfila():
    email = session["email"]
    korisnik = getKorisnik(email)
    return render_template('IzmeniProfil.html', korisnik = korisnik)


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


    cursor = mysql.connection.cursor()
    cursor.execute(''' INSERT INTO korisnik (ime, prezime, adresa, grad, drzava, brojTelefona, email, lozinka, verifikovan, stanjeNaRacunu, stanjeUBanci) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',(ime, prezime, adresa, grad, drzava, brojTelefona, email, lozinka, verifikovan, stanjeNaRacunu, stanjeUBanci))
    mysql.connection.commit()
    cursor.close()

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
    kartica = getKartica(brojKartice)
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
        return  render_template("/Index.html", korisnik = korisnik1)
    else:
        poruka = "Nemate dovoljno novca na bankovnom racunu"
        return render_template("/Depozit.html", errormsg=poruka)



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

def povezivanjeKarticeiKorisnika(email : str, ime : str, brojKartice : str, datumIsteka : str, kod : str, stanjeNaRacunu):
    cursor = mysql.connection.cursor()
    cursor.execute(''' INSERT INTO kartica (ime, brojKartice, datumIsteka, kod) VALUES ( %s, %s, %s ,%s)''', (ime, brojKartice, datumIsteka, kod,))
    cursor.execute(''' UPDATE korisnik SET brojKartice = %s, verifikovan = 1, stanjeNaRacunu = stanjeNaRacunu - 1 WHERE email = %s''', (brojKartice, email,))
    mysql.connection.commit()
    cursor.close()

def IzmeniStanja(email: str, stanjeNaRacunu : int, stanjeUBanci : int):
    cursor = mysql.connection.cursor()
    cursor.execute(''' UPDATE korisnik SET stanjeNaRacunu = %s, stanjeUBanci = %s WHERE email = %s ''', (stanjeNaRacunu,stanjeUBanci,email,))
    mysql.connection.commit()
    cursor.close()


def verifikujKorisnika(email):
    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE korisnik SET verifikovan = 1 WHERE email = %s", (email,))
    mysql.connection.commit()
    cursor.close()


def izmeniKorisnika(email, ime, prezime, adresa, grad, drzava, brojTelefona, lozinka):
    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE korisnik SET ime = %s, prezime = %s, adresa = %s, grad = %s, drzava = %s, brojTelefona = %s, lozinka = %s WHERE email = %s", (ime, prezime, adresa, grad, drzava, brojTelefona, lozinka, email,))
    mysql.connection.commit()
    cursor.close()



def updateKorisnika(email, ime, prezime, adresa, grad, drzava, brojTelefona, lozinka, stanjeNaRacunu, stanjeUBanci):
    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE korisnik SET ime = %s, prezime = %s, adresa = %s, grad = %s, drzava = %s, brojTelefona = %s, lozinka = %s, stanjeNaRacunu = %s, stanjeUBanci = %s WHERE email = %s", (ime, prezime, adresa, grad, drzava, brojTelefona, lozinka, stanjeNaRacunu, stanjeUBanci, email,))
    mysql.connection.commit()
    cursor.close()



if __name__ == '__main__':
    app.run(debug=True)
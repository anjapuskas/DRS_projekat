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


@app.route("/PrikaziRegistraciju", methods=['POST', 'GET'])
def prikaziRegistraciju():
     return render_template('Registracija.html')


@app.route("/PrikaziIzmenuProfila", methods=['POST', 'GET'])
def prikaziIzmenuProfila():
     return render_template('IzmeniProfil.html')


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

    cursor = mysql.connection.cursor()
    cursor.execute(''' INSERT INTO korisnik (ime, prezime, adresa, grad, drzava, brojTelefona, email, lozinka, verifikovan) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)''',(ime, prezime, adresa, grad, drzava, brojTelefona, email, lozinka, verifikovan))
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
    email = request.form['inputEmail']


    email1 = session["email"]

    if email == email1:
        izmeniKorisnika(email, ime, prezime, adresa, grad, drzava, brojTelefona, lozinka)
        poruka = "Uspesna modifikacija"
        return render_template("Index.html", errormsg = poruka)
    else:
        poruka = "NIJE DOBRO"
        return render_template("Login.html", errormsg=poruka)






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
            return render_template("Index.html", korisnik = '')
    else:
        poruka = "Nespravan email ili lozinka!"
    return render_template("Login.html", errormsg=poruka)


@app.route("/Verifikacija", methods=['GET', 'POST'])
def verifikacija():
    ime = request.form['inputIme']
    brojKartice = request.form['inputBrojKartice']
    datum = request.form['inputDatum']
    kod = request.form['inputKod']
    email = session["email"]

    korisnik = getKorisnik(email)

    if korisnik != None and korisnik["ime"] == ime and brojKartice == "4242424242424242" and datum == "02/23" and kod == "123":
        #poruka = "Uspesno logovanje!"
        verifikujKorisnika(email)
        return render_template("Index.html")
    else:
        poruka = "Neuspesno logovanje"
        return render_template("Verifikacija.html", errormsg=poruka)


def getKorisnik(email: str) -> dict:
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM korisnik WHERE email = %s", (email,))
    korisnik = cursor.fetchone()
    cursor.close()
    return korisnik

def verifikujKorisnika(email):
    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE korisnik SET verifikovan = 1 WHERE email = %s", (email,))
    mysql.connection.commit()
    cursor.close()


def izmeniKorisnika(email, ime, prezime, adresa, grad, drzava, brojTelefona, lozinka):
    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE korisnik SET ime = %s, prezime = %s, adresa = %s, grad = %s, drzava = %s, brojTelefona = %s, lozinka = %s WHERE email = %s", (ime, prezime, adresa, grad, drzava, brojTelefona, lozinka, email))
    mysql.connection.commit()
    cursor.close()


if __name__ == '__main__':
    app.run(debug=True)
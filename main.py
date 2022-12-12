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

@app.route("/Registracija", methods=['GET', 'POST'])
def registracija():
    global korisnici

    ime = request.form['inputIme']
    prezime = request.form['inputPrezime']
    adresa = request.form['inputAdresa']
    grad = request.form['inputGrad']
    drzava = request.form['inputDrzava']
    brojTelefona = request.form['inputBrojTelefona']
    email = request.form['inputEmail']
    lozinka = request.form['inputLozinka']


    cursor = mysql.connection.cursor()
    cursor.execute(''' INSERT INTO korisnik (ime, prezime, adresa, grad, drzava, brojTelefona, email, lozinka) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)''',(ime, prezime, adresa, grad, drzava, brojTelefona, email, lozinka))
    mysql.connection.commit()
    cursor.close()

    return render_template("Login.html")


@app.route("/Login", methods=['GET', 'POST'])
def login():
    email = request.form['inputEmail']
    lozinka = request.form['inputLozinka']

    user = getUser(email)

    if user != None and user["email"] == email and user["lozinka"] == lozinka:
        #poruka = "Uspjesno logovanje!"
        session["email"] = email
        return render_template("Verifikacija.html")
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

    user = getUser(email)

    print(email)
    print(user != None)

    if user != None and user["ime"] == ime and brojKartice == "4242424242424242" and datum == "02/23" and kod == "123":
        #user["verifikovan"] = 1
        poruka = "Uspesno logovanje!"
        return render_template("Verifikacija.html", errormsg=poruka)
    else:
        poruka = "Neuspesno logovanje"
        return render_template("Verifikacija.html", errormsg=poruka)


def getUser(email: str) -> dict:
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM korisnik WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()
    return user



if __name__ == '__main__':
    app.run(debug=True)
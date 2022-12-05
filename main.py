from flask import Flask, request, session, render_template
app = Flask(__name__)

korisnici = []


@app.route("/")
def start():
    return render_template("Registracija.html")


@app.route("/Login", methods=['post', 'get'])
def login():
     return render_template('Login.html')



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

    for k in korisnici:
        if k["email"] == email:
            poruka = "Korisnik sa datim email-om vec posotji!"
            return render_template("Registracija.html", errormsg = poruka)


    k = {
        "ime" : ime,
        "prezime" : prezime,
        "adresa" : adresa,
        "grad" : grad,
        "drzava" : drzava,
        "brojTelefona" : brojTelefona,
        "email" : email,
        "lozinka" : lozinka
    }

    korisnici.append(k)
    return render_template("Login.html")




if __name__ == '__main__':
    app.run(debug=True)
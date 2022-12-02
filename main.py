from flask import Flask, request, session, render_template
app = Flask(__name__)

@app.route("/")
def start():
    return render_template("Registracija.html")


@app.route("/Login", methods=['post', 'get'])
def login():
     return render_template('Login.html')


if __name__ == '__main__':
    app.run(debug=True)
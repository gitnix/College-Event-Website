from flask import Flask, render_template, json, request,redirect,session
from flask.ext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'secret'

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'password'
app.config['MYSQL_DATABASE_DB'] = 'eventwebsite'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)


@app.route('/')
def main():
    return render_template('index.html')

#route defs must be same name as route!

@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/signUp')
def signUp():
    return render_template('signup.html')

@app.route('/signIn')
def signIn():
    return render_template('signin.html')


if __name__=='__main__':
    app.run(debug=True)
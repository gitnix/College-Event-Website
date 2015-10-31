from flask import Flask, render_template, json, request, redirect, session, \
    flash, url_for
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

@app.route('/userHome')
def userHome():
    return render_template('userhome.html')

@app.route('/validateSignIn',methods=['POST'])
def validateSignIn():
    try:
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']

        #let's call MySQL
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_validateSignIn',(_email,))
        data = cursor.fetchall()

        if len(data)>0:
            #make sure to update this line if schema changes
            #currently password is located as the 3rd column in users table
            if check_password_hash(str(data[0][2]), _password):
                session['user'] = data[0][0]
                return redirect('/userHome')
            else:
                flash("Invalid Password")
                render_template('signin.html')
        flash("That email is not registered")
        return render_template('signin.html')

    except Exception as e:
        return json.dumps({'Exception error':str(e)})
    finally:
        cursor.close()
        conn.close()

@app.route('/validateSignUp', methods=['POST'])
def validateSignUp():
    try:
        _firstname = request.form['inputFirstName']
        _lastname = request.form['inputLastName']
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']
            
        #let's call MySQL
        conn = mysql.connect()
        cursor = conn.cursor()
        _hashed_password = generate_password_hash(_password)
        cursor.callproc('sp_createUser',(_firstname,_lastname,_email,_hashed_password))
        data = cursor.fetchall()

        if len(data) is 0:
            conn.commit()
            return redirect('/userHome')
        else:
            flash("That Email is already registered")
        return render_template('/signup.html')

    except Exception as e:
        return json.dumps({'Exception error':str(e)})
    finally:
        cursor.close() 
        conn.close()

@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect('/')


if __name__=='__main__':
    app.run(debug=True)
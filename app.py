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

#use the def name when calling the route through code

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signin')
def signin():
    return render_template('signin.html')

@app.route('/userhome')
def userhome():
    if session.get('user'):
        return render_template('userhome.html')
    else:
        return render_template('error.html', error="You must be logged in to access this page.")

@app.route('/validate_signin', methods=['POST'])
def validate_signin():
    try:
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']

        #let's call MySQL
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_validate_signin', (_email,))
        data = cursor.fetchall()

        if len(data) > 0:
            #make sure to update this line if schema changes
            #currently password is located as the 3rd column in users table
            if check_password_hash(str(data[0][2]), _password):
                session['user'] = data[0][0]
                return redirect('/userhome')
            else:
                flash("Invalid Password")
                return render_template('signin.html')
        flash("That email is not registered")
        return render_template('signin.html')

    except Exception as err:
        return json.dumps({'Exception error':str(err)})
    finally:
        cursor.close()
        conn.close()

@app.route('/validate_signup', methods=['POST'])
def validate_signup():
    try:
        _firstname = request.form['inputFirstName']
        _lastname = request.form['inputLastName']
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']

        #let's call MySQL
        conn = mysql.connect()
        cursor = conn.cursor()
        _hashed_password = generate_password_hash(_password)
        cursor.callproc('sp_create_user', (_firstname, _lastname, _email, _hashed_password))
        data = cursor.fetchall()

        if len(data) is 0:
            conn.commit()
            return render_template('signin.html', create=True)
        else:
            flash("That Email is already registered")
        return render_template('/signup.html')

    except Exception as err:
        return json.dumps({'Exception error':str(err)})
    finally:
        cursor.close()
        conn.close()

@app.route('/eventmaker')
def create_event():
    return render_template('eventmaker.html')

@app.route('/validate_event', methods=['POST'])
def validate_event():
    try:
        _eventName = request.form['eventName']
        _eventType = request.form['eventType']
        _eventDescription = request.form['eventDescription']
        _eventEmail = request.form['eventEmail']
        _eventPhone = request.form['eventPhone']

        #let's call MySQL
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_create_event', (_eventName, _eventType, _eventDescription, _eventEmail, _eventPhone))
        data = cursor.fetchall()

        if len(data) is 0:
            conn.commit()
            flash("The event has been created.", 'alert-success')
            return render_template('userhome.html')
        else:
            flash("That event is already set up!", 'alert-warning')
        return render_template('eventmaker.html')

    except Exception as err:
        return json.dumps({'Exception error':str(err)})
    finally:
        cursor.close()
        conn.close()

@app.route('/signout')
def signout():
    session.pop('user', None)
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)

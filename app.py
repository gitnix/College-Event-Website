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
    if session.get('user'):
        return redirect('/userhome')
    return render_template('index.html')

#use the def name when calling the route through code

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signin')
def signin():
    if session.get('user'):
        return render_template('userhome')
    return render_template('signin.html')

@app.route('/userhome')
def userhome():
    if session.get('user'):
        _event = session.get('eventviewtype')

        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_get_events_by_type', (_event, ))
        events = cursor.fetchall()

        events_dict = []
        for event in events:
            event_dict = {
                '1_Id': event[0],
                'aTitle': event[1],
                'bDescription': event[2],
                '4_Date': event[4]
            }
            events_dict.append(event_dict)

        return render_template('userhome.html', events = events_dict)
    else:
        return render_template('error.html', error="You must be logged in to access this page.")

@app.route('/messages')
def messages():
    if session.get('user'):
        _user = session.get('user')

        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_get_messages_by_user', (_user, ))
        messagelist = cursor.fetchall()

        return render_template('messages.html', messages = messagelist)
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
                session['eventviewtype'] = 'd'
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
            flash("Account Created!", 'alert-success')
            return render_template('signin.html')
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
            # return render_template('userhome.html')
            return redirect('/userhome')
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

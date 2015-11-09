from flask import Flask, render_template, json, request, redirect, session, \
    flash, url_for
from flask.ext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash
import logging

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
        return render_template('userhome.html')
    return render_template('signin.html')

@app.route('/userhome')
def userhome():
    try:
        if session.get('user'):
            _event = session.get('eventviewtype')

            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_get_events_by_type', (_event, ))
            events = cursor.fetchall()

            events_list = []
            for event in events:
                event_item = [
                    event[1], event[3], event[0]
                ]
                events_list.append(event_item)

            cursor.close()
            conn.close()

            return render_template('userhome.html', events = events_list)
        else:
            return render_template('error.html', error="You must be logged in to access this page.")
    except Exception as err:
        return json.dumps({'Exception error':str(err)})

@app.route('/event/<eventid>')
def show_event_profile(eventid):
    # show the event profile for that event
    try:    
        if session.get('user'):
            # _event_id = eventid   
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_get_event', (eventid, ))
            eventdata = cursor.fetchall()

            for eventinfo in eventdata:
                #in order it is:
                #Name, Description, Email, Phone
                event_data = [
                    eventinfo[1], eventinfo[3], eventinfo[4], eventinfo[5]
                ]

                cursor.close()
                conn.close()

            return render_template('event.html', eventinfo = event_data)
        else:
            return render_template('error.html', error="You must be logged in to access this page.")

    except Exception as err:
        return json.dumps({'Exception error':str(err)})
        
@app.route('/messages')
def messages():
    try:
        if session.get('user'):
            _user = session.get('user')
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_get_messages_by_user', (_user, ))
            
            # message_data = cursor.fetchall()

            # messages_dict = []
            # for message in message_data:
            #     message_dict = {
            #         'Header': message[0],
            #         'Content': message[1]
            #     }
            #     messages_dict.append(message_dict)

            message_list = cursor.fetchall()
            logging.warning(message_list)
            messages_to_insert = []
            for message in message_list:
                message_item = [
                    # the order of these is determined by the select sql in the stored procedure
                    # message_id, header, content, recepient id
                    message[0], message[1], message[2], message[4]
                ]
                messages_to_insert.append(message_item)
            logging.warning(messages_to_insert)

            cursor.close()
            conn.close()

            return render_template('messages.html', messages_data = messages_to_insert)
        else:
            return render_template('error.html', error="You must be logged in to access this page.")
    except Exception as err:
        return json.dumps({'Exception error':str(err)})
    
@app.route('/createmessage')
def create_message():
    return render_template('messagemaker.html')

@app.route('/deletemessage/<messageid>')
def delete_message(messageid):
    if session.get('user'):
        _userid = session.get('user')
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_delete_message', (messageid, _userid))
        data = cursor.fetchall()

        if len(data) is 0:
            conn.commit()
            cursor.close()
            conn.close()
            flash("Message Deleted!", 'alert-success')
            return redirect('/messages')
        else:
            cursor.close()
            conn.close()
            flash("This can't be done")
            return render_template('error.html')

    else:
        return render_template('error.html', error="You do not have permission to perform this action OK.")


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
                session['eventviewtype'] = 'public'
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
        return render_template('signup.html')

    except Exception as err:
        return json.dumps({'Exception error':str(err)})
    finally:
        cursor.close()
        conn.close()

@app.route('/eventmaker')
def create_event():
    if session.get('user'):
        return render_template('eventmaker.html')
    else:
        return render_template('error.html', error="You must be logged in to access this page.")

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
            cursor.close()
            conn.close()
            # return render_template('userhome.html')
            return redirect('/userhome')
        else:
            flash("That event is already set up!", 'alert-warning')
            cursor.close()
            conn.close()
        return render_template('eventmaker.html')

    except Exception as err:
        return json.dumps({'Exception error':str(err)})

@app.route('/signout')
def signout():
    session.pop('user', None)
    return redirect('/')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error="We're sorry. We could not find the requested page.")


if __name__ == '__main__':
    app.run(debug=True)

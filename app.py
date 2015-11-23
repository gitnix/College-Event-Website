from flask import Flask, render_template, json, request, redirect, session, \
    flash, url_for
from flask.ext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash
from datetime import datetime
import logging

mysql = MySQL()
app = Flask(__name__)
# app.config.from_envvar('universityapp_settings')
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
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.callproc('sp_get_universities', )
    universities = cursor.fetchall()

    university_array = []
    for university in university_array:
        university_item = [
            university[0], university[1], university[2]
        ]
        university_array.append(university_item)

    cursor.close()
    conn.close()
    return render_template('signup.html', university_list = universities)

@app.route('/signin')
def signin():
    if session.get('user'):
        return render_template('userhome.html')
    return render_template('signin.html')

@app.route('/userhome')
def userhome():
    try:
        if session.get('user'):

            _viewby = session.get('event-view-type')
            logging.warning(_viewby)
            _sortby = session.get('event-sort-type')
            _userFirstName = session.get('user-first-name')
            _userLastName = session.get('user-last-name')
            _userUniversity = session.get('user-university')
        
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_get_events_by_type_sort', (_viewby, _sortby, _userUniversity))
            events = cursor.fetchall()

            events_list = []
            for event in events:
                event_item = [
                    event[1], event[3], event[0]
                ]
                events_list.append(event_item)

            cursor.close()
            conn.close()

            return render_template('userhome.html', events=events_list)
        else:
            return render_template('error.html', error="You must be logged in to access this page.")
    except Exception as err:
        return json.dumps({'Exception error':str(err)})


@app.route('/change_type', methods=['POST'])
def change_type_sort():
    _type = request.form['eventType']
    session['event-view-type'] = _type
    logging.warning("We are now in change_type")
    logging.warning(session.get('event-view-type'))
    logging.warning("we are still in change_type")
    # return render_template('userhome.html')
    return redirect('/userhome')

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

            if len(eventdata) is 0:
                conn.commit()
                cursor.close()
                conn.close()
                return render_template('error.html', error="Page does not exist")


            for eventinfo in eventdata:
                #in order it is:
                #Name, Description, Email, Phone, Loacation, startdate, endDate
                event_data = [
                    eventinfo[1], eventinfo[3], eventinfo[4], eventinfo[5], eventinfo[6], eventinfo[7], eventinfo[8]
                ]

            edate_start = event_data.pop(5)
            new_edate_start = datetime.strftime(edate_start, '%m/%d/%Y %I:%M %p')
            event_data.append(new_edate_start)

            edate_end = event_data.pop(5)
            new_edate_end = datetime.strftime(edate_end, '%m/%d/%Y %I:%M %p')
            event_data.append(new_edate_end)

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
            _sort = session.get('message-sort')
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_get_messages_by_user', (_user, _sort ))
            
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

@app.route('/createrso')
def create_rso():
    return render_template('rsomaker.html')

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
                session['event-view-type'] = 'public'
                session['event-sort-type'] = 'event_date'
                session['user_role'] = data[0][3]
                session['user-first-name'] = data[0][4]
                session['user-last-name'] = data[0][5]
                session['message-sort'] = 'message_id'
                session['user-university'] = data[0][6]
                session['user-email'] = data[0][1]
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
        _universityid = request.form['universitySelector']

        #let's call MySQL
        conn = mysql.connect()
        cursor = conn.cursor()
        _hashed_password = generate_password_hash(_password)
        cursor.callproc('sp_create_user', (_firstname, _lastname, _email, _hashed_password, _universityid))
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



@app.route('/validate_university', methods=['POST'])
def validate_university():
    try:
        _universityname = request.form['universityName']
        _universitylocation = request.form['universityLocation']
        _universitydomain = request.form['universityDomain']

        #let's call MySQL
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_create_university', (_universityname, _universitylocation, _universitydomain))
        data = cursor.fetchall()

        if len(data) is 0:
            conn.commit()
            flash("University Created!", 'alert-success')
            return render_template('userhome.html')
        else:
            flash("That University is already registered")
        return render_template('universitymaker.html')

    except Exception as err:
        return json.dumps({'Exception error':str(err)})
    finally:
        cursor.close()
        conn.close()

@app.route('/createevent')
def create_event():
    if session.get('user_role') in ('admin', 'super_admin'):
        _userEmail = session.get('user-email')
        logging.warning(_userEmail)
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_get_rsos_of_admin', (_userEmail, ))
        rsos_list = cursor.fetchall()
        logging.warning(rsos_list)
        # conn.commit()
        rsos_array = []
        for rso in rsos_list:
            rso_item = rso[0]
            rsos_array.append(rso_item)
        cursor.close()
        conn.close()
        return render_template('eventmaker.html', rsos_list = rsos_array)
    else:
        return render_template('error.html', error="You must be logged in to access this page.")

@app.route('/createuniversity')
def create_university():
    if session.get('user_role') == 'super_admin':
        return render_template('universitymaker.html')
    else:
        return render_template('error.html', error="You do not have the rights to access this page.")

@app.route('/validate_event', methods=['POST'])
def validate_event():
    try:
        _eventName = request.form['eventName']
        _eventType = request.form['eventType']
        _eventDescription = request.form['eventDescription']
        _eventEmail = request.form['eventEmail']
        _eventPhone = request.form['eventPhone']
        _eventLocation = request.form['eventLocation']
        _eventStart = request.form['eventStart']
        _eventEnd = request.form['eventEnd']

        _eventrso = request.form['rsoSelector']
        _eventuniversity = session.get('user-university')


        date_object = datetime.strptime(_eventStart, '%m/%d/%Y %I:%M %p')
        date_object2 = datetime.strptime(_eventEnd, '%m/%d/%Y %I:%M %p')



        #let's call MySQL
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_create_event', (_eventName, _eventType, _eventDescription, _eventEmail, _eventPhone, _eventLocation, date_object, date_object2, _eventuniversity, _eventrso))
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

@app.route('/validate_rso', methods=['POST'])
def validate_rso():
    try:
        _user1 = request.form['rsoEmail1']
        _user2 = request.form['rsoEmail2']
        _user3 = request.form['rsoEmail3']
        _user4 = request.form['rsoEmail4']
        _user5 = request.form['rsoEmail5']
        _name = request.form['rsoName']
        _description = request.form['rsoDescription']
        _email = request.form['rsoEmail']
        _phone = request.form['rsoPhone']

        _rsouniversity = session.get('user-university')
        _mainEmail = session.get('user-email')

        #let's call MySQL
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_create_rso', (_mainEmail, _user1, _user2, _user3, _user4, _user5, _name, _description, _email, _phone, _rsouniversity))
        data = cursor.fetchall()

        if len(data) is 0:
            conn.commit()
            # conn = mysql.connect()
            # cursor = conn.cursor()
            cursor.callproc('sp_insert_into_rso', (_mainEmail, _user1, _user2, _user3, _user4, _user5, _name))
            flash("RSO set up!", 'alert-success')
            conn.commit()
            cursor.close()
            conn.close()
            return render_template('eventmaker.html')

        else:
            conn.commit()
            flash("Not all valid users.", 'alert-warning')
            cursor.close()
            conn.close()
            # return render_template('userhome.html')
            return render_template('rsomaker.html')

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
    app.run(debug = True)

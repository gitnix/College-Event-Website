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

#holder for time being
@app.route('/validateLogin',methods=['POST'])
def validateLogin():
    return render_template('index.html')

#holder for time being
@app.route('/validateSignIn',methods=['POST'])
def validateSignIn():
    return render_template('index.html')

@app.route('/validateSignUp', methods=['POST'])
def validateSignUp():
    try:
        _firstname = request.form['inputFirstName']
        _lastname = request.form['inputLastName']
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']

        # validate the received values
        if _firstname and _lastname and _email and _password:
            
            # All Good, let's call MySQL
            
            conn = mysql.connect()
            cursor = conn.cursor()
            _hashed_password = generate_password_hash(_password)
            cursor.callproc('sp_createUser',(_firstname,_lastname,_email,_hashed_password))
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                return json.dumps({'message':'User created successfully !'})
            else:
                return json.dumps({'error':str(data[0])})
        else:
            return json.dumps({'html':'<span>Enter the required fields</span>'})

    except Exception as e:
        return json.dumps({'Exceptio error':str(e)})
    finally:
        cursor.close() 
        conn.close()

#not yet implemented
@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect('/')


if __name__=='__main__':
    app.run(debug=True)
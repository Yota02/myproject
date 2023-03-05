from flask import request, Flask, session, render_template, flash, redirect, url_for
from datetime import datetime
import mysql.connector
from werkzeug.utils import secure_filename
import os
from flask_mysqldb import MySQL,MySQLdb
import MySQLdb.cursors

app = Flask(__name__)

cnx = mysql.connector.connect(host = 'localhost',
                              user = 'root',
                              password = '',
                              database = 'bdmain')

app.secret_key = '74$mo7iokz&qmhfgg35r+641a(vqw4pkfdp7bl4ogqimv2*9pj'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'bdmain'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

cur = cnx.cursor()

img = os.path.join('static', 'uploads')

with app.app_context():
    cur1 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/upload_avatar')
def upload_avatar():
    return render_template('upload_avatar.html')

@app.route('/update', methods =['GET', 'POST'])
def update():
    if request.method == 'POST' :
        mail = session['mail']
        pseudo = request.form.get('pseudo')
        mdp = request.form.get('password')
        mail2 = request.form.get('mail')
        val = mail2, pseudo, mdp, mail
        sql = "UPDATE user SET mail = %s, pseudo = %s, password = %s WHERE mail = %s"
        cur.execute(sql, val)
        mysql.connection.commit()
        cur.close()
        return render_template('index.html')
    else :
        return render_template('update.html')
    
@app.route("/login", methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' :
        mail = request.form['mail']
        password = request.form['password']
        cur.execute('SELECT * FROM user WHERE mail = %s AND password = %s', (mail, password))
        account = cur.fetchone() 
        if account:
            session['loggedin'] = True
            session['id'] = account[0]
            session['mail'] = account[1]
            session['pseudo'] = account[2]
            session['date'] = account[4]
            msg = 'Logged in successfully !'
            return render_template('index.html', msg = msg)
        else:
            msg = 'Incorrect pseudo / password !'
        return render_template('login.html', msg = msg)
    else : 
        return render_template('login.html')
    
@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route("/param")
def param():
    return render_template('param.html')

@app.route("/avatar")
def avatar():
    file = os.path.join(img, session['avatar'])
    return file

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('mail', None)
    session.pop('id', None)
    session.pop('pseudo', None)
    session.pop('date', None)
    session.pop('avatar', None)
    session.pop('pp', None)
    return redirect(url_for('index'))

@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' :
        pseudo = request.form.get('pseudo')
        mdp = request.form.get('password')
        mail = request.form.get('mail')
        date = datetime.now()
        cur.execute('SELECT * FROM user WHERE mail = %s AND password = %s', (mail, mdp))
        account = cur.fetchone()
        cur.close()
        if account:
            msg = 'Account already exists !'
        else:
            val = mail, pseudo, mdp, date
            sql = "INSERT INTO user (mail, pseudo, password, date) VALUES (%s, %s, %s, %s)"
            cur.execute(sql, val)
            mysql.connection.commit()
            cur.close()
            msg = 'You have successfully registered !'
    else:
        if 'pseudo' in session:
            return redirect(url_for('index'))
    return render_template('index.html', msg = msg)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404

@app.route('/delete')
def delete():
    mail = session['mail']
    sql = f"DELETE FROM user WHERE mail = '{mail}'"
    cur.execute(sql)
    cur.close()
    print("suppréssion réussis")
    logout()
    return render_template('index.html') 

def allowed_file(filename):
 return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
 
@app.route("/upload",methods=["POST","GET"])
def upload():
    cursor = mysql.connection.cursor()
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    now = datetime.now()
    if request.method == 'POST':
        files = request.files.getlist('files[]')
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                cur.execute("INSERT INTO images (file_name, uploaded_on) VALUES (%s, %s)",[filename, now])
                mysql.connection.commit()
        cur.close()   
        flash('File(s) successfully uploaded')    
    return redirect('/')

@app.route('/display/<filename>')
def display_image(filename):
    return redirect(url_for('static', filename='uploads/' + filename), code=301)

@app.route("/upload_pp",methods=["POST","GET"])
def upload_pp():
    id = session['id']
    cursor = mysql.connection.cursor()
    cur1 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    now = datetime.now()
    if request.method == 'POST':
            files = request.files.getlist('files[]')
            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    cur1.execute("INSERT INTO avatar (id, file_name, uploaded_on) VALUES (%s, %s, %s)",[id, filename, now])
                    mysql.connection.commit()
                    session['pp'] = True
                    session['avatar'] = filename
            cur1.close()   
            flash('File(s) successfully uploaded')    
    return redirect('param')

@app.route("/modif_pp",methods=["POST","GET"])
def modif_pp():
    id = session['id']
    cursor = mysql.connection.cursor()
    cur1 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    now = datetime.now()
    if request.method == 'POST':
            files = request.files.getlist('files[]')
            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    cur1.execute("UPDATE avatar SET file_name = %s, uploaded_on = %s WHERE id = %s",[filename, now, id])
                    mysql.connection.commit()
                    session['pp'] = True
                    session['avatar'] = filename
            cur1.close()   
            flash('File(s) successfully uploaded')    
    return redirect('param')

if __name__=='__main__':
    app.run(debug= True)

cur.close()





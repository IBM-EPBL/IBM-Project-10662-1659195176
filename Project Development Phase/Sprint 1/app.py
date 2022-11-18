from datetime import datetime

import ibm_db
from flask import Flask, redirect, render_template, request, url_for,session
from flask_cors import CORS, cross_origin
from flask_mail import Mail, Message

app = Flask(__name__, template_folder = 'templates',static_folder='static')
app.config['SECRET_KEY'] = 'top-secret!'
app.config['MAIL_SERVER'] = 'smtp.sendgrid.net'#
app.config['MAIL_PORT'] = 111 #
app.config['MAIL_USE_TLS'] = True #
app.config['MAIL_USERNAME'] = 'abikey' #
app.config['MAIL_PASSWORD'] = 'personalexpensetracker@123' #
app.config['MAIL_DEFAULT_SENDER'] = 'personalexpensetrackercse@gmail.com' #
mail = Mail(app)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# GLobal variables
EMAIL=''
ID=''
USERNAME=''


conn=ibm_db.connect("DATABASE=bludb;HOSTNAME=54a2f15b-5c0f-46df-8954-7e38e612c2bd.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32733;Security=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=vzd06788;PWD=8heOP6PmppzV7gEm;","","")
                   





@app.route("/")
def home():
    return render_template("index.html")

@app.route('/registration', methods=['GET', 'POST'])
@cross_origin()
def registration():
    if request.method=='GET':
        return render_template('registration.html')
    msg = ''
    if request.method == 'POST' :
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        EMAIL=email
        sql="SELECT * FROM PETA_USER1 WHERE EMAIL=?"
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.execute(stmt)
        account=ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            msg = 'Account already exists !'
            return render_template('registration.html', msg = msg)
        else:
            sql="INSERT INTO PETA_USER1(USERNAME,EMAIL,PASSWORD) VALUES(?,?,?)"
            stmt=ibm_db.prepare(conn,sql)
            ibm_db.bind_param(stmt,1,username)
            ibm_db.bind_param(stmt,2,email) 
            ibm_db.bind_param(stmt,3,password)
            ibm_db.execute(stmt)
            msg = 'You have successfully registered !'
            return render_template('registration.html', msg = msg)
 

@app.route('/login',methods=['GET','POST'])
def login():
    msg = ''
    global USERNAME
    global ID
    
    if request.method=='POST':
        email=request.form['email']
        password=request.form['password']
        sql="SELECT * FROM PETA_USER1 WHERE email=? AND password=?"
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.bind_param(stmt,2,password)
        result=ibm_db.execute(stmt)
        print(result)
        account=ibm_db.fetch_row(stmt)
        print(account)
        
        param = "SELECT * FROM PETA_USER1 WHERE email = " + "\'" + email + "\'" + " and password = " + "\'" + password + "\'"
        res = ibm_db.exec_immediate(conn, param)
        dictionary = ibm_db.fetch_assoc(res)
        if account:
            if account:
                session['loggedin'] = True
                session['id'] = dictionary["ID"]
                ID = dictionary["ID"]
                session['username'] = dictionary["USERNAME"]
                USERNAME= dictionary["USERNAME"]
                session['email'] = dictionary["EMAIL"]
            
                return redirect('/dashboard')

        else:
            msg = 'Wrong mail or password !'
            return render_template('login.html', msg = msg)
    if request.method=='GET':
        return render_template('login.html')
    
    
    

@app.route('/dashboard', methods=['GET'])
def dashboard():
    if ID=='' and USERNAME=='':
        return render_template('login.html')
    
    param = "SELECT * FROM expenses WHERE userid = " + str(session['id']) + " AND DATE(date) =DATE(current timestamp) ORDER BY date DESC"
    res = ibm_db.exec_immediate(conn, param)
    dictionary = ibm_db.fetch_assoc(res)
    expense = []
    while dictionary != False:
        temp = []
        temp.append(dictionary["ID"])
        temp.append(dictionary["USERID"])
        temp.append(dictionary["DATE"])
        temp.append(dictionary["EXPENSENAME"])
        temp.append(dictionary["AMOUNT"])
        temp.append(dictionary["PAYMODE"])
        temp.append(dictionary["CATEGORY"])
        expense.append(temp)
        print(temp)
        dictionary = ibm_db.fetch_assoc(res)
    return render_template('dashboard.html',expense=expense,msg=session['username'])
      
   
if __name__=='__main__':
    app.run( debug=True)
    
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
      


@app.route('/addexpense', methods=['GET', 'POST'])
def add_expense():
    if request.method=='GET':        
        return render_template('addexpense.html',msg=session['username'])
    
    
    if request.method == 'POST': 
        date = request.form['date']
        expensename = request.form['expensename']
        amount = request.form['amount']
        paymode = request.form['paymode']
        category = request.form['category']
        
        print(date)
        p1 = date[0:10]
        p2 = date[11:13]
        p3 = date[14:]
        p4 = p1 + "-" + p2 + "." + p3 + ".00"
        print(p4)
        sql="INSERT INTO EXPENSES(userid,date,expensename,amount,paymode,category) VALUES(?,?,?,?,?,?)"
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,session['id'])
        ibm_db.bind_param(stmt,2,p4)
        ibm_db.bind_param(stmt,3,expensename)
        ibm_db.bind_param(stmt,4,amount)
        ibm_db.bind_param(stmt,5,paymode)
        ibm_db.bind_param(stmt,6,category)
        ibm_db.execute(stmt)
        
        print("Expenses added")

        param = "SELECT * FROM expenses WHERE userid = " + str(session['id']) + " AND MONTH(date) = MONTH(current timestamp) AND YEAR(date) = YEAR(current timestamp) ORDER BY date DESC"
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
        total=0
        for x in expense:
            total += x[4]

        param = "SELECT id, limitss FROM limits WHERE userid = " + str(session['id']) + " ORDER BY id DESC LIMIT 1"
        res = ibm_db.exec_immediate(conn, param)
        dictionary = ibm_db.fetch_assoc(res)
        row = []
        s = 0
        while dictionary != False:
            temp = []
            temp.append(dictionary["LIMITSS"])
            row.append(temp)
            dictionary = ibm_db.fetch_assoc(res)
            s = temp[0]

        #if total > int(s):
            #msg = "Hello " + session['username'] + " , " + "you have crossed the monthly limit of Rs. " + s + "/- !!!" + "\n" + "Thank you, " + "\n" + "Team Personal Expense Tracker."  
            #sendmail(msg,session['email'])  
        
        return redirect("/display")
    
@app.route("/display")
def display():
    print(session["username"],session['id'])
    
    # cursor = mysql.connection.cursor()
    # cursor.execute('SELECT * FROM expenses WHERE userid = % s AND date ORDER BY `expenses`.`date` DESC',(str(session['id'])))
    # expense = cursor.fetchall()

    param = "SELECT * FROM expenses WHERE userid = " + str(session['id']) + " ORDER BY date DESC"
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
        
    param = "SELECT * FROM expenses WHERE userid = " + str(session['id']) + " ORDER BY date DESC"
    res = ibm_db.exec_immediate(conn, param)
    dictionary = ibm_db.fetch_assoc(res)
    expense1 = []
    while dictionary != False:
        temp = []
        temp.append(dictionary["ID"])
        temp.append(dictionary["USERID"])
        temp.append(dictionary["DATE"])
        temp.append(dictionary["EXPENSENAME"])
        temp.append(dictionary["AMOUNT"])
        temp.append(dictionary["PAYMODE"])
        temp.append(dictionary["CATEGORY"])
        expense1.append(temp)
        print(temp)
        dictionary = ibm_db.fetch_assoc(res)
        
        
    total=0
    t_food=0
    t_entertainment=0
    t_business=0
    t_rent=0
    t_EMI=0
    t_other=0
 
     
    for x in expense1:
        total += x[4]
        if x[6] == "food":
            t_food += x[4]
        
        elif x[6] == "entertainment":
            t_entertainment  += x[4]
    
        elif x[6] == "business":
            t_business  += x[4]
        elif x[6] == "rent":
            t_rent  += x[4]
        
        elif x[6] == "EMI":
            t_EMI  += x[4]
        
        elif x[6] == "other":
            t_other  += x[4]
            
    print(total)
    print(t_food)
    print(t_entertainment)
    print(t_business)
    print(t_rent)
    print(t_EMI)
    print(t_other)


    
    return render_template('display.html',msg=session['username'],expense = expense,  total = total ,
                        t_food = t_food,t_entertainment =  t_entertainment,
                        t_business = t_business,  t_rent =  t_rent, 
                        t_EMI =  t_EMI,  t_other =  t_other )
 


@app.route('/delete/<string:id>', methods = ['POST', 'GET' ])
def delete(id):
    #  cursor = mysql.connection.cursor()
    #  cursor.execute('DELETE FROM expenses WHERE  id = {0}'.format(id))
    #  mysql.connection.commit()

    param = "DELETE FROM expenses WHERE  id = " + id
    res = ibm_db.exec_immediate(conn, param)

    print('deleted successfully')    
    return redirect("/display")
 
    
#UPDATE---DATA

@app.route('/edit/<id>', methods = ['POST', 'GET' ])
def edit(id):
    # cursor = mysql.connection.cursor()
    # cursor.execute('SELECT * FROM expenses WHERE  id = %s', (id,))
    # row = cursor.fetchall()

    param = "SELECT * FROM expenses WHERE  id = " + id
    res = ibm_db.exec_immediate(conn, param)
    dictionary = ibm_db.fetch_assoc(res)
    row = []
    while dictionary != False:
        temp = []
        temp.append(dictionary["ID"])
        temp.append(dictionary["USERID"])
        temp.append(dictionary["DATE"])
        temp.append(dictionary["EXPENSENAME"])
        temp.append(dictionary["AMOUNT"])
        temp.append(dictionary["PAYMODE"])
        temp.append(dictionary["CATEGORY"])
        row.append(temp)
        print(temp)
        dictionary = ibm_db.fetch_assoc(res)

    print(row[0])
    return render_template('edit.html',msg=session['username'] ,expenses = row[0])




@app.route('/update/<id>', methods = ['POST'])
def update(id):
  if request.method == 'POST' :
   
      date = request.form['date']
      expensename = request.form['expensename']
      amount = request.form['amount']
      paymode = request.form['paymode']
      category = request.form['category']
    
    #   cursor = mysql.connection.cursor()
    #   cursor.execute("UPDATE `expenses` SET `date` = % s , `expensename` = % s , `amount` = % s, `paymode` = % s, `category` = % s WHERE `expenses`.`id` = % s ",(date, expensename, amount, str(paymode), str(category),id))
    #   mysql.connection.commit()

      p1 = date[0:10]
      p2 = date[11:13]
      p3 = date[14:]
      p4 = p1 + "-" + p2 + "." + p3 + ".00"

      sql = "UPDATE expenses SET date = ? , expensename = ? , amount = ?, paymode = ?, category = ? WHERE id = ?"
      stmt = ibm_db.prepare(conn, sql)
      ibm_db.bind_param(stmt, 1, p4)
      ibm_db.bind_param(stmt, 2, expensename)
      ibm_db.bind_param(stmt, 3, amount)
      ibm_db.bind_param(stmt, 4, paymode)
      ibm_db.bind_param(stmt, 5, category)
      ibm_db.bind_param(stmt, 6, id)
      ibm_db.execute(stmt)

      print('successfully updated')
      return redirect("/display")

@app.route("/limit" )
def limit():
    return redirect('/limitn')
    

@app.route("/limitnum" , methods = ['POST' ])
def limitnum():
     if request.method == "POST":
        number= request.form['number']
        sql = "INSERT INTO limits (userid, limitss) VALUES (?, ?)"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, session['id'])
        ibm_db.bind_param(stmt, 2, number)
        ibm_db.execute(stmt)

        return redirect('/limitn')
     
         
@app.route("/limitn") 
def limitn():
    param = "SELECT id, limitss FROM limits WHERE userid = " + str(session['id']) + " ORDER BY id DESC LIMIT 1"
    res = ibm_db.exec_immediate(conn, param)
    dictionary = ibm_db.fetch_assoc(res)
    row = []
    s = 0
    while dictionary != False:
        temp = []
        temp.append(dictionary["LIMITSS"])
        row.append(temp)
        dictionary = ibm_db.fetch_assoc(res)
        s = temp[0]
    
    return render_template("limit.html",msg=session['username'] , y= s)

#REPORT

@app.route("/today")
def today():
    sql = "SELECT date,amount FROM expenses WHERE userid = " + str(session['id']) + "  AND DATE(date) =DATE(current timestamp) ORDER BY date DESC"
    stmt = ibm_db.exec_immediate(conn, sql)
    dummy = ibm_db.fetch_assoc(stmt)
    texpense = []
    while dummy != False:
        temp = []
        temp.append(dummy["DATE"])
        temp.append(dummy["AMOUNT"])
        texpense.append(temp)
        print(temp)
        dummy = ibm_db.fetch_assoc(stmt)
    
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


    total=0
    t_food=0
    t_entertainment=0
    t_business=0
    t_rent=0
    t_EMI=0
    t_other=0

    
    for x in expense:
        total += x[4]
        if x[6] == "food":
            t_food += x[4]
        
        elif x[6] == "entertainment":
            t_entertainment  += x[4]
    
        elif x[6] == "business":
            t_business  += x[4]
        elif x[6] == "rent":
            t_rent  += x[4]
        
        elif x[6] == "EMI":
            t_EMI  += x[4]
        
        elif x[6] == "other":
            t_other  += x[4]
        
    print(total)
    
    print(t_food)
    print(t_entertainment)
    print(t_business)
    print(t_rent)
    print(t_EMI)
    print(t_other)


    
    return render_template("today.html",msg=session['username'], texpense = texpense, expense = expense,  total = total ,
                        t_food = t_food,t_entertainment =  t_entertainment,
                        t_business = t_business,  t_rent =  t_rent, 
                        t_EMI =  t_EMI,  t_other =  t_other )
     

@app.route("/month")
def month():
    sql = "SELECT DATE,AMOUNT FROM expenses WHERE userid = " + str(session['id']) + "  AND MONTH(DATE) = MONTH(current timestamp) ORDER BY DATE DESC"
    stmt = ibm_db.exec_immediate(conn, sql)
    dummy1 = ibm_db.fetch_assoc(stmt)
    texpense = []
    while dummy1 != False:
        temp = []
        temp.append(dummy1["DATE"])
        temp.append(dummy1["AMOUNT"])
        texpense.append(temp)
        print(temp)
        dummy1 = ibm_db.fetch_assoc(stmt)

    
    param = "SELECT * FROM expenses WHERE userid = " + str(session['id']) + " AND MONTH(date) = MONTH(current timestamp) ORDER BY date DESC"
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
        
        
    total=0
    t_food=0
    t_entertainment=0
    t_business=0
    t_rent=0
    t_EMI=0
    t_other=0
 
     
    for x in expense:
        total += x[4]
        if x[6] == "food":
            t_food += x[4]
        
        elif x[6] == "entertainment":
            t_entertainment  += x[4]
    
        elif x[6] == "business":
            t_business  += x[4]
        elif x[6] == "rent":
            t_rent  += x[4]
        
        elif x[6] == "EMI":
            t_EMI  += x[4]
        
        elif x[6] == "other":
            t_other  += x[4]
            
    print(total)
    print(t_food)
    print(t_entertainment)
    print(t_business)
    print(t_rent)
    print(t_EMI)
    print(t_other)


    
    return render_template("month.html",msg=session['username'], texpense = texpense, expense = expense,  total = total ,
                        t_food = t_food,t_entertainment =  t_entertainment,
                        t_business = t_business,  t_rent =  t_rent, 
                        t_EMI =  t_EMI,  t_other =  t_other )
 
     
         
@app.route("/year")
def year():
    sql = "SELECT DATE,AMOUNT FROM expenses WHERE userid = " + str(session['id']) + "   AND YEAR(date) = YEAR(current timestamp) ORDER BY DATE DESC"
    stmt = ibm_db.exec_immediate(conn, sql)
    dummy1 = ibm_db.fetch_assoc(stmt)
    texpense = []
    while dummy1 != False:
        temp = []
        temp.append(dummy1["DATE"])
        temp.append(dummy1["AMOUNT"])
        texpense.append(temp)
        print(temp)
        dummy1 = ibm_db.fetch_assoc(stmt)
        
    param = "SELECT * FROM expenses WHERE userid = " + str(session['id']) + " AND YEAR(date) = YEAR(current timestamp) ORDER BY date DESC"
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

  
    total=0
    t_food=0
    t_entertainment=0
    t_business=0
    t_rent=0
    t_EMI=0
    t_other=0
 
    
    for x in expense:
        total += x[4]
        if x[6] == "food":
            t_food += x[4]
        
        elif x[6] == "entertainment":
            t_entertainment  += x[4]
    
        elif x[6] == "business":
            t_business  += x[4]
        elif x[6] == "rent":
            t_rent  += x[4]
        
        elif x[6] == "EMI":
            t_EMI  += x[4]
        
        elif x[6] == "other":
            t_other  += x[4]
        
    print(total)
    print(t_food)
    print(t_entertainment)
    print(t_business)
    print(t_rent)
    print(t_EMI)
    print(t_other)


     
    return render_template("year.html",msg=session['username'], texpense = texpense, expense = expense,  total = total ,
                        t_food = t_food,t_entertainment =  t_entertainment,
                        t_business = t_business,  t_rent =  t_rent, 
                        t_EMI =  t_EMI,  t_other =  t_other )

#log-out

@app.route('/signout')

def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return render_template('index.html')

     
      
if __name__=='__main__':
    app.run( debug=True)
    
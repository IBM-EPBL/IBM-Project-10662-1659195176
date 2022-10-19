from email.mime import base
from flask import Flask,redirect,url_for,render_template,request,session,flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
app=Flask(__name__)
appli_context = app.app_context()
app.secret_key ="hello"
app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime =timedelta(minutes=1)


db.init_app(app)
class users(db.Model):
    __tablename__ = 'users'
    id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))

    def __init__(self, name, email):
        self.name = name
        self.email = email

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/view")
def view():
    return render_template("view.html", values=users.query.all())

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/content")
def content():
    return render_template("content.html")


@app.route("/login", methods=["POST","GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        user= request.form["nm"]
        session["user"]= user
        found_user =users.query.filter_by(name=user).first()
        if found_user:
            session["email"]=found_user.email

        else:
            usr = users(user,None)
            db.session.add(usr)
            db.session.commit()
        flash("login successful!")
        return redirect(url_for("user"))
    else:
        if "user" in session:
             flash("Already loged in!")
             return redirect(url_for("user"))
        return render_template("login.html")

@app.route("/user",methods=["POST","GET"])
def user():
    email =None
    if "user" in session:
        user =session["user"]
        if request.method == "POST":
            email =request.form["email"]
            session["email"]=email
            found_user =users.query.filter_by(name=user).first()
            found_user.email = email
            db.session.commit()
            flash("email was saved")
        else:
            if "email" in session:
                email = session["email"]
        return render_template("user.html",email=email)
    else:
         flash("you are not logged in!")
         return redirect(url_for("login"))

@app.route("/logout")
def logout():
    flash("you have been logged out!","info")
    session.pop("user", None)
    session.pop("email", None)
    return redirect(url_for("login"))
     
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(port=5000,debug=True)
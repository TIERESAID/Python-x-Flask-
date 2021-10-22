from logging import error, info
from flask import Flask, render_template,flash,redirect,url_for,session,logging,request
from data import Articles
import sqlite3
from flask import g
from wtforms import Form , StringField, TextAreaField, PasswordField , validators
from passlib.hash import sha256_crypt

app = Flask(__name__)

DATABASE = "flaskapp.db"

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


Articles = Articles()

@app.route("/")
def index():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/articles")
def articles():
    return render_template("articles.html", articles = Articles)

@app.route("/article/<string:id>/")
def article(id):
    return render_template("article.html", id = id)

class Registerform(Form):
    name = StringField( "Name", [validators.Length(min=1, max=50)] )
    username = StringField( "Username",[validators.Length(min=4 , max=50)] )
    email = StringField("Email",[validators.Length(min=6, max=50)])
    password = PasswordField(
        "Password", 
        [validators.data_required(),
        validators.EqualTo("confirm", message = "Password do not match")
        ]
    )
    confirm = PasswordField("Confirm Password")
    
@app.route("/register", methods=["GET","POST"])
def register():
    form = Registerform(request.form)
    if request.method == "POST" and form.validate() :
        try:

            name = form.name.data
            email = form.email.data
            username = form.username.data
            password = sha256_crypt.encrypt(str(form.password.data))

            # create cursor 
            db = get_db()
            cur = db.cursor()
            cur.execute( "INSERT INTO users(name , email,username,password) VALUES (?,?,?,?)",(name, email,username,password) )

            db.commit()
            flash("Registered succes , you can now logging", "success")
        except:
            db.rollback()
            flash("error in insertion operation", "error")
        finally:
            close_connection()
            redirect(url_for("loggin"))
    return render_template("register.html", form = form)

# user login
@app.route("/login", methods =["GET", "POST"])
def loggin():
    error = ""
    if request.method == "POST":
        # Get form field 
        username = request.form["username"]
        password_candidate = request.form["password"]

        # create a cursor
        db = get_db()
        db.row_factory = sqlite3.Row
        cur = db.cursor()
        # get user by username
        cur.execute("""SELECT * FROM users WHERE username = ?""",[username])
        data = cur.fetchone()
        if(data):
            #Get stored hash
            password = data["password"]

            #Compare the password
            if sha256_crypt.verify(password_candidate,password):
                app.logger,info("PASSWORD MATCHED")
            else:
                error = "Invalid Password"
        else:
            error = "Username not found"
            render_template("login.html", error = error)
    return render_template("login.html", error = error)

if __name__ == "__main__":
    app.secret_key = "1234"
    app.run(debug=True)
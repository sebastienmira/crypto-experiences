from flask import Flask, flash, url_for, redirect, render_template, request, session
from flask_session import Session
import crypto
import io
from helpers import apology, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from cs50 import SQL

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db= SQL("sqlite:///crypto.db")

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/encrypt', methods=["GET","POST"])
def encrypt():
    if request.method =="POST":
        plain=request.form.get("plain")
        key=request.form.get("key")
        
        try:
            encrypted=crypto.substitution(plain,key)
            return render_template('encrypt.html', encrypted=encrypted, plain=plain, key=key)
        except ValueError as err:
            error=str(err)
            return render_template('encrypt.html', error=error, plain=plain, key=key)
    return render_template("encrypt.html")

@app.route('/decrypt', methods=["GET","POST"])
def decrypt():
    mode = request.form.get("mode", "known")  # Default to "known" if not provided
    encrypted = request.form.get("encrypted", "")
    key = request.form.get("key", "a")
    attempt = request.form.get("attempts")
    keylength=request.form.get("keylength")
    plain = ""
    error = ""
    

    if request.method =="POST":
        
        if mode=='known':
            try:
                plain=crypto.desubstitution(encrypted,key)
                return render_template('decrypt.html', plain=plain, encrypted=encrypted, key=key, mode=mode)
            except ValueError as err:
                error=str(err)
                return render_template('decrypt.html', error=error, encrypted=encrypted, key=key,mode=mode)
        
        elif mode=='caeser':
            if attempt:
                guesses=crypto.guessCaeser(encrypted,attempts=int(attempt))
                return render_template('decrypt.html', plain=guesses, encrypted=encrypted, mode=mode)
            else:
                render_template("decrypt.html", mode=mode)
        
        elif mode=='vigenere':
            if attempt and keylength:
                guesses=crypto.guessVigenere(encrypted, key_length=int(keylength), attempts=int(attempt))
                return render_template('decrypt.html', plain=guesses, encrypted=encrypted, mode=mode)
            else:
                return render_template("decrypt.html", mode=mode)


    return render_template("decrypt.html", mode=mode)

@app.route("/analysis", methods=["GET","POST"])
def analysis():
    if request.method =="POST":
        encrypted=request.form.get("encrypted")
        analysis=crypto.frequencyAnalysis(encrypted)
        
        img=io.BytesIO()
        crypto.histFreqAnalysis(encrypted).savefig(img, format='png')
        img.seek(0)

        img_path = 'static/images/analysis.png'
        with open(img_path, 'wb') as f:
            f.write(img.getbuffer())

        return render_template("analysis.html", analysis=analysis, img_path=img_path)
    return render_template("analysis.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
    

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    session.clear()

    if request.method == "POST":
        if not request.form.get("username"):
            return apology("must provide username", 400)

        elif not request.form.get("password"):
            return apology("must provide password", 400)

        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords don't match", 400)

        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        if len(rows) != 0:
            return apology("username already exists", 400)

        db.execute("INSERT INTO users (username, hash) VALUES(?,?)", request.form.get(
            "username"), generate_password_hash(request.form.get("password")))

        session["user_id"] = db.execute(
            "SELECT id FROM users WHERE username=?", request.form.get("username"))[0]["id"]
        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/chat", methods=["GET", "POST"])
@login_required
def search():
   if request.method=="POST":
       user=request.form.get("user")
       return redirect(url_for("chat",user=user))
   else:
       return render_template("chatsearch.html")
   
@app.route("/chat/<user>", methods=["GET", "POST"])
@login_required
def chat(user):
   if request.method=="POST":
       return render_template("chat.html", user=user)
   else:
       return render_template("chat.html", user=user)


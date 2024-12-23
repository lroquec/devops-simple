from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import hashlib
import os
from dotenv import load_dotenv

app = Flask(__name__)

# Secret key for session management (using environment variable for Docker compatibility)
# app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]  # NOSONAR
load_dotenv()

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

# Database connection details (using environment variables for Docker compatibility)
app.config["MYSQL_HOST"] = os.getenv("MYSQL_HOST")
app.config["MYSQL_USER"] = os.getenv("MYSQL_USER", "root")
app.config["MYSQL_PASSWORD"] = os.getenv("MYSQL_PASSWORD", "")
app.config["MYSQL_DB"] = os.getenv("MYSQL_DB", "pythonlogin")

# Initialize MySQL
mysql = MySQL(app)


@app.route("/")
def index():
    return redirect(url_for("login"))


@app.route("/login/", methods=["GET", "POST"])
def login():
    msg = ""
    if (
        request.method == "POST"
        and "username" in request.form
        and "password" in request.form
    ):
        username = request.form["username"]
        password = request.form["password"]

        # Hash the provided password using SHA1
        hashed_password = hashlib.sha1(password.encode()).hexdigest()

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            "SELECT * FROM accounts WHERE username = %s AND password = %s",
            (username, hashed_password),
        )
        account = cursor.fetchone()
        if account:
            session["loggedin"] = True
            session["id"] = account["id"]
            session["username"] = account["username"]
            session["role"] = account["role"]  # Retrieve role from database
            return redirect(url_for("home"))
        else:
            msg = "Incorrect username/password!"
    return render_template("index.html", msg=msg)


@app.route("/login/logout")
def logout():
    session.pop("loggedin", None)
    session.pop("id", None)
    session.pop("username", None)
    return redirect(url_for("login"))


@app.route("/login/register", methods=["GET", "POST"])
def register():
    msg = ""
    if (
        request.method == "POST"
        and "username" in request.form
        and "password" in request.form
        and "email" in request.form
    ):
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]
        role = "user"  # Default role for all registrations

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM accounts WHERE username = %s", (username,))
        account = cursor.fetchone()
        if account:
            msg = "Account already exists!"
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            msg = "Invalid email address!"
        elif not re.match(r"[A-Za-z0-9]+", username):
            msg = "Username must contain only characters and numbers!"
        elif not username or not password or not email:
            msg = "Please fill out the form!"
        else:
            # Hash the password using SHA1
            hashed_password = hashlib.sha1(password.encode()).hexdigest()

            # Insert into the database
            cursor.execute(
                "INSERT INTO accounts (username, password, email, role) VALUES (%s, %s, %s, %s)",
                (username, hashed_password, email, role),
            )
            mysql.connection.commit()
            msg = "You have successfully registered!"
    elif request.method == "POST":
        msg = "Please fill out the form!"
    return render_template("register.html", msg=msg)


@app.route("/login/home")
def home():
    if "loggedin" in session:
        return render_template("home.html", username=session["username"])
    return redirect(url_for("login"))


@app.route("/login/profile")
def profile():
    if "loggedin" in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM accounts WHERE id = %s", (session["id"],))
        account = cursor.fetchone()
        return render_template("profile.html", account=account)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

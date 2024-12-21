from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import os
from functools import wraps  # For route protection


app = Flask(__name__)

# Secret key for session management
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]

# Database connection details
app.config["MYSQL_HOST"] = os.getenv("MYSQL_HOST", "db")
app.config["MYSQL_USER"] = os.getenv("MYSQL_USER", "root")
app.config["MYSQL_PASSWORD"] = os.getenv("MYSQL_PASSWORD", "example")
app.config["MYSQL_DB"] = os.getenv("MYSQL_DB", "pythonlogin")

# Initialize MySQL
mysql = MySQL(app)

# Test database connection at application startup
with app.app_context():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SHOW DATABASES;")
        databases = cursor.fetchall()
        print("Databases available:", databases)
    except Exception as e:
        print("Error connecting to the database:", str(e))

@app.route("/")
def index():
    return redirect(url_for("login"))

# Authentication decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("loggedin") or session.get("role") != "admin":
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


# Login route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            "SELECT * FROM accounts WHERE username = %s AND password = SHA1(%s)",
            (username, password),
        )
        account = cursor.fetchone()
        if account:
            session["loggedin"] = True
            session["id"] = account["id"]
            session["username"] = account["username"]
            session["role"] = account["role"]
            return redirect(url_for("list_users"))
        else:
            return "Invalid username or password."
    return render_template("login.html")


# Logout route
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/users", methods=["GET"])
@admin_required
def list_users():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM accounts")
        users = cursor.fetchall()
        return render_template("users.html", users=users)
    except Exception as e:
        print(f"Error fetching users: {str(e)}")  # Log the error
        return (
            render_template(
                "error.html", message="An error occurred while fetching users."
            ),
            500,
        )


@app.route("/add_user", methods=["GET", "POST"])
@admin_required
def add_user():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]
        role = request.form["role"]

        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            # Check for valid email format
            if "@" not in email or "." not in email:
                return "Invalid email format. Please try again."

            # Check if username is already taken
            cursor.execute("SELECT * FROM accounts WHERE username = %s", (username,))
            if cursor.fetchone():
                return "Username already exists. Please choose another."

            # Check if email is already registered
            cursor.execute("SELECT * FROM accounts WHERE email = %s", (email,))
            if cursor.fetchone():
                return "Email already exists. Please choose another."

            # Insert user into the database
            cursor.execute(
                "INSERT INTO accounts (username, password, email, role) VALUES (%s, SHA1(%s), %s, %s)",
                (username, password, email, role),
            )
            mysql.connection.commit()
            return redirect(url_for("list_users"))
        except Exception as e:
            return f"An error occurred: {str(e)}"
    return render_template("add_user.html")


@app.route("/edit_user/<int:user_id>", methods=["GET", "POST"])
@admin_required
def edit_user(user_id):
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if request.method == "POST":
            username = request.form["username"]
            email = request.form["email"]
            role = request.form["role"]
            password = request.form["password"]

            # Check for valid email format
            if "@" not in email or "." not in email:
                return "Invalid email format. Please try again."

            # Check if username is already taken (excluding current user)
            cursor.execute(
                "SELECT * FROM accounts WHERE username = %s AND id != %s",
                (username, user_id),
            )
            if cursor.fetchone():
                return "Username already exists. Please choose another."

            # Check if email is already registered (excluding current user)
            cursor.execute(
                "SELECT * FROM accounts WHERE email = %s AND id != %s", (email, user_id)
            )
            if cursor.fetchone():
                return "Email already exists. Please choose another."

            # Update user with or without password
            if password:  # If a new password is provided
                cursor.execute(
                    "UPDATE accounts SET username = %s, email = %s, role = %s, password = SHA1(%s) WHERE id = %s",
                    (username, email, role, password, user_id),
                )
            else:
                cursor.execute(
                    "UPDATE accounts SET username = %s, email = %s, role = %s WHERE id = %s",
                    (username, email, role, user_id),
                )

            mysql.connection.commit()
            return redirect(url_for("list_users"))
        else:
            cursor.execute("SELECT * FROM accounts WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            if user:
                return render_template("edit_user.html", user=user)
            else:
                return f"User with ID {user_id} not found."
    except Exception as e:
        return f"An error occurred: {str(e)}"


@app.route("/delete_user/<int:user_id>", methods=["POST"])
@admin_required
def delete_user(user_id):
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # Delete user from the database
        cursor.execute("DELETE FROM accounts WHERE id = %s", (user_id,))
        mysql.connection.commit()
        return redirect(url_for("list_users"))
    except Exception as e:
        return f"An error occurred: {str(e)}"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

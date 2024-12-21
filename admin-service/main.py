from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
import MySQLdb.cursors
import os

app = Flask(__name__)

# Secret key for session management
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_secret_key')

# Database connection details
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', 'example')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'pythonlogin')

# Initialize MySQL
mysql = MySQL(app)

@app.route('/users', methods=['GET'])
def list_users():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts')
        users = cursor.fetchall()
        return render_template('users.html', users=users)
    except Exception as e:
        return f"An error occurred: {str(e)}"

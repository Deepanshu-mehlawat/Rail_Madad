from flask import Flask, render_template, request, redirect, url_for, flash
from flask_bcrypt import Bcrypt
import pymongo
from pymongo import MongoClient

app = Flask(__name__)
uri = "mongodb+srv://deepanshumehlawat2003:m7E9EiYSSDHhI3z9@sih.0oetq.mongodb.net/?retryWrites=true&w=majority&appName=sih"
bcrypt = Bcrypt(app)

# Create a new client and connect to the server
client = MongoClient(uri)
db = client['SIH']
users_collection = db['Users']

@app.route('/')
def home():
    return redirect('/login')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = users_collection.find_one({'email': email})

        if user and bcrypt.check_password_hash(user['password'], password):
            return redirect('/sih')
        else:
            return render_template('login.html', message='Username or password incorrect')
    return render_template('login.html', message='Login to Continue')

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Check if user already exists
        if users_collection.find_one({'email': email}):
            return render_template('register.html', message='Account already exists. Login to continue.')
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        users_collection.insert_one({'username': username, 'email': email, 'password': hashed_password, 'type':0})
        return render_template('login.html', message='Account created! Login to continue')
    
    return render_template('register.html', message='Please register')

# SIH route (Protected)
@app.route('/sih')
def sih():
    # Add logic for authenticated users
    return render_template('sih.html')

if __name__ == '__main__':
    app.run(debug=True)

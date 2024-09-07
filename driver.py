from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import pymongo
import json
from pymongo import MongoClient
import prompts
import os
from PIL import Image
#from IPython.display import Image
#from IPython.core.display import HTML
import google.generativeai as genai

app = Flask(__name__)
uri = "mongodb+srv://deepanshumehlawat2003:m7E9EiYSSDHhI3z9@sih.0oetq.mongodb.net/?retryWrites=true&w=majority&appName=sih"
bcrypt = Bcrypt(app)
load_dotenv()
api_key = os.getenv('API_KEY')
genai.configure(api_key=api_key)

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

@app.route('/cat_img', methods=['POST'])
def cat_img():
    if 'image' not in request.files:
        return jsonify({"type": "0"})  # No image received
    
    image_file = request.files['image']
    
    try:
        image = Image.open(image_file)  # Open the uploaded image
    except IOError:
        return jsonify({"type": "0"})

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content([prompts.prompt1, image])

    # Print response.text to debug
    print('Response text from model:', response.text)
    
    try:
        # Attempt to parse the response as JSON
        response_json = json.loads(response.text)
    except json.JSONDecodeError:
        # If parsing fails, return a default error response
        return jsonify({"type": "0"})
    
    # Return the parsed JSON response
    return jsonify(response_json)

@app.route('/cat_text',methods=['POST'])
def cat_text():
    if 'text' not in request.form:
        return jsonify({"type": "0"})

    text = request.form['text']
    print(text)
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompts.prompt2+text)

    print('Response text from model:', response.text)
    
    try:
        # Attempt to parse the response as JSON
        response_json = json.loads(response.text)
    except json.JSONDecodeError:
        # If parsing fails, return a default error response
        return jsonify({"type": "0"})
    
    # Return the parsed JSON response
    return jsonify(response_json)


if __name__ == '__main__':
    app.run(debug=True)

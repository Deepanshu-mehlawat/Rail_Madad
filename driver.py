from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import pymongo
import uuid
import json
from pymongo import MongoClient
import prompts
import os
from PIL import Image
import re
import io
#from IPython.display import Image
#from IPython.core.display import HTML
import google.generativeai as genai

app = Flask(__name__)
uri = "mongodb+srv://deepanshumehlawat2003:m7E9EiYSSDHhI3z9@sih.0oetq.mongodb.net/?retryWrites=true&w=majority&appName=sih"
bcrypt = Bcrypt(app)
load_dotenv()
api_key = os.getenv('API_KEY')
genai.configure(api_key=api_key)
app.secret_key = os.urandom(24) 

# Create a new client and connect to the server
client = MongoClient(uri)
db = client['SIH']
users_collection = db['Users']
complaints_collection = db['Complaints']

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect('/sih')
    return redirect('/login')


# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = users_collection.find_one({'email': email})

        if user and bcrypt.check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])  # Storing user_id in session
            session['username'] = user['username']
            if user.get('type') == 1:
                return redirect('/admin_login')  # Redirect to admin login page
            else:
                return redirect('/sih')  # Redirect to 'sih' page
        else:
            return render_template('login.html', message='Username or password incorrect')
    return render_template('login.html', message='Login to Continue')

# Logout route
@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Clear session data
    session.pop('username', None)
    return redirect('/login')

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
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('sih.html', username=session.get('username'))

def clean_and_parse_json(response_text):
    fence_pattern = r'```(?:json)?\s*({.*?})\s*```'
    match = re.search(fence_pattern, response_text, re.DOTALL | re.IGNORECASE)

    json_str = None
    if match:
        json_str = match.group(1)
    else:
        start_index = response_text.find('{')
        end_index = response_text.rfind('}')

        if start_index != -1 and end_index != -1 and end_index > start_index:
            json_str = response_text[start_index : end_index + 1]
        else:
            # If no '{' or '}' found, or in wrong order, assume the whole text MIGHT be JSON
            # This is a fallback and might fail if there's surrounding text
            json_str = response_text.strip()

    if not json_str:
        print("Error: Could not extract a potential JSON string.")
        return None

    try:
        # Attempt to parse the extracted string
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        # Include the string we *tried* to parse for better debugging
        print(f"--- Original text was ---\n{response_text}\n---")
        print(f"--- Attempted parsing ---\n{json_str}\n---")
        return None # Indicate failure clearly


@app.route('/cat_img', methods=['POST'])
def cat_img():
    if 'image' not in request.files:
        flash('No image file received.')
        return jsonify({"type": "0", "error": "No image file received."})

    image_file = request.files['image']
    if image_file.filename == '':
        flash('No image selected.')
        return jsonify({"type": "0", "error": "No image selected."})

    try:
        # It's safer to read bytes and let GenAI handle it, or ensure valid image with PIL
        image_bytes = image_file.read()
        image = Image.open(io.BytesIO(image_bytes)) # Validate it's an image
    except Exception as e: # Catch broader exceptions during image processing
        print(f"Error processing image file: {e}")
        return jsonify({"type": "0", "error": f"Invalid image file: {e}"})

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        # Pass PIL image object directly
        response = model.generate_content([prompts.prompt1, image])

        # Use the helper function to parse
        parsed_data = clean_and_parse_json(response.text)

        if parsed_data is None:
             # Parsing failed, return default error response
             print("JSON parsing failed in cat_img.")
             return jsonify({"type": "0", "error": "Failed to parse AI response"})

        # Return the parsed JSON response
        return jsonify(parsed_data)

    except Exception as e:
        print(f"Error during Gemini API call or processing in cat_img: {e}")
        # Provide a more informative error if possible
        return jsonify({"type": "0", "error": f"API or processing error: {str(e)}"})


@app.route('/cat_text', methods=['POST'])
def cat_text():
    if 'text' not in request.form or not request.form['text'].strip():
        return jsonify({"type": "0", "error": "No text received or text is empty."})

    text = request.form['text']
    print("Received text for categorization:", text) # Log received text

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        # Construct the full prompt
        full_prompt = prompts.prompt2 + "\n\nUser Complaint Text:\n" + text
        response = model.generate_content(full_prompt)

        # Use the helper function to parse
        parsed_data = clean_and_parse_json(response.text)

        if parsed_data is None:
            # Parsing failed, return default error response
            print("JSON parsing failed in cat_text.")
            return jsonify({"type": "0", "error": "Failed to parse AI response"})

        # Return the parsed JSON response
        return jsonify(parsed_data)

    except Exception as e:
        print(f"Error during Gemini API call or processing in cat_text: {e}")
        return jsonify({"type": "0", "error": f"API or processing error: {str(e)}"})

    
@app.route('/admin_login')
def admin_login():
    if not session.get('user_id'):
        return redirect('/login')

    try:
        # Define severity mapping for sorting (High -> 1, Medium -> 2, Low -> 3)
        severity_order = {'high': 1, 'medium': 2, 'low': 3}

        # Retrieve and sort pending complaints (status = 0) by severity
        pending_complaints = list(
            complaints_collection.find({'status': 0}).sort(
                [("severity", 1)]  # Sort by severity, lower is prioritized
            )
        )

        # Retrieve and sort active complaints (status = 1) by severity
        active_complaints = list(
            complaints_collection.find({'status': 1}).sort(
                [("severity", 1)]  # Sort by severity, lower is prioritized
            )
        )

        # Pass the complaints and status options to the template
        return render_template('admin_page.html', 
                               pending_complaints=pending_complaints, 
                               active_complaints=active_complaints,
                               here={1: "approved", 2: "disapproved", 0: "pending"})

    except Exception as e:
        print(f'Error loading complaints: {e}')
        return jsonify({'success': False, 'error': str(e)})

@app.route('/add_complaint', methods=['POST'])
def add_complaint():
    try:
        data = request.json
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'User not logged in'}), 401 # Unauthorized

        # Generate a unique complaint ID
        complaint_id = str(uuid.uuid4())

        # Prepare the base data
        complaint_data = {
            'complaint_id': complaint_id,
            'user_id': user_id,
            'name': data.get('name'),
            'email': data.get('email'),
            'pnr': data.get('pnr'),
            'incident_date_time': data.get('incidentDateTime'),
            'type': data.get('type'),
            'sub_type': data.get('subType'),
            'message': data.get('message'),
            'severity': 'Pending Analysis', # Default before API call
            'department': 'Pending Analysis',# Default before API call
            'status': 0 # Default status: pending
        }

        # --- Call Gemini API to get severity and department ---
        # Ensure type and message are present for the prompt
        complaint_type = data.get('type', 'N/A')
        complaint_message = data.get('message', 'No details provided.')
        prompt_input = f"Type: {complaint_type}\nSubtype: {data.get('subType', 'N/A')}\nDetails: {complaint_message}"

        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompts.prompt3 + "\n" + prompt_input)

            # Use the helper function to parse
            response_json = clean_and_parse_json(response.text)

            if response_json is None:
                 # Handle parsing failure - log and use defaults or specific error values
                 print("JSON parsing failed for severity/department in add_complaint.")
                 # Keep default 'Pending Analysis' or set specific error status
                 complaint_data['severity'] = 'Error: Parsing Failed'
                 complaint_data['department'] = 'Error: Parsing Failed'
            else:
                 # Successfully parsed - update values safely using .get()
                 complaint_data['severity'] = response_json.get('severity', 'Analysis Incomplete')
                 complaint_data['department'] = response_json.get('department', 'Analysis Incomplete')

        except Exception as e:
            print(f"Error during Gemini API call for severity/department: {e}")
            # Handle API call failure - log and use defaults or error status
            complaint_data['severity'] = 'Error: API Failed'
            complaint_data['department'] = 'Error: API Failed'
        # --- End Gemini API call ---


        # Save to MongoDB
        complaints_collection.insert_one(complaint_data)

        return jsonify({'success': True, 'complaint_id': complaint_id})

    except Exception as e:
        # Catch general errors in the route logic
        print(f'Error in add_complaint route: {e}')
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

@app.route('/status', methods=['POST'])
def status():
    try:
        data = request.get_json()
        complaint_id = data.get('complaint_id')
        new_status = data.get('status')  # 1 for approve, 2 for disapprove
        
        if not complaint_id or new_status not in [1, 2]:
            return jsonify({'success': False, 'message': 'Invalid data'}), 400
        
        # Update the status in the database
        result = complaints_collection.update_one(
            {'complaint_id': complaint_id},
            {'$set': {'status': new_status}}
        )
        
        if result.modified_count == 1:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Complaint not found or no update made'}), 404
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/dashboard')
def dashboard():
    try:
        # Retrieve the user's requests from MongoDB
        user_id = session['user_id']  # Define this based on your authentication method
        
        # Define severity mapping for sorting (High -> 1, Medium -> 2, Low -> 3)
        severity_order = {'high': 1, 'medium': 2, 'low': 3}

        # Retrieve and sort user requests by severity
        user_requests = list(
            complaints_collection.find({'user_id': user_id}).sort(
                [("severity", 1)]  # Sort by severity, lower values (1 = high) come first
            )
        )
        
        # Pass the requests to the template
        return render_template('dashboard.html', 
                               user_requests=user_requests, 
                               here={1: "approved", 2: "disapproved", 0: "pending"})
    except Exception as e:
        print(f'Error loading user requests: {e}')
        return jsonify({'success': False, 'error': str(e)})


@app.route('/save_changes', methods=['POST'])
def save_changes():
    try:
        data = request.json
        complaint_id = data['complaint_id']
        
        # Debugging to see the received data
        print(f"Received data: {data}")
        print(f"Complaint ID: {complaint_id}")

        # Perform the update in MongoDB
        result = complaints_collection.update_one(
            {'complaint_id': complaint_id},  # Match complaint ID
            {
                '$set': {
                    'type': data['type'],
                    'severity': data['severity'],
                    'department': data['department']
                }
            }
        )
        
        # Check if the document was actually modified
        if result.matched_count == 0:
            print(f"No document found with complaint_id: {complaint_id}")
            return jsonify({'success': False, 'message': 'No matching document found'})
        else:
            print(f"Document updated for complaint_id: {complaint_id}")
            return jsonify({'success': True})

    except Exception as e:
        print(f"Error while saving changes: {e}")
        return jsonify({'success': False, 'message': str(e)})




if __name__ == '__main__':
    app.run(debug=True)

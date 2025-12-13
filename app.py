from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os
from services.service import Service

# --- Configuration ---
app = Flask(__name__)
JSON_FILE = 'data.json'

services = Service()

# --- JSON Utility Functions (Unchanged) ---
def load_users():
    """Loads existing user data from the JSON file."""
    if not os.path.exists(JSON_FILE):
        return []
    try:
        with open(JSON_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_users(users):
    """Writes user data back to the JSON file."""
    with open(JSON_FILE, 'w') as f:
        json.dump(users, f, indent=4)

# --- Routes ---

@app.route('/')
def index():
    """Renders the main login/signup page."""
    users = load_users()
    user_emails = [user['email'] for user in users]
    return render_template('index.html', user_emails=user_emails)

@app.route('/create_user', methods=['POST'])
def create_user():
    """Handles the account creation (Sign Up) process, now including role."""
    email = request.form.get('email')
    password = request.form.get('password')
    # --- NEW: Get the selected role from the form data ---
    role = request.form.get('role') 
    
    users = load_users()

    if not email or not password or not role:
        # Check if role is missing too
        return jsonify({'success': False, 'message': 'Email, Password, and Role are required.'}), 400

    if any(user['email'] == email for user in users):
        return jsonify({'success': False, 'message': 'Account already exists with this email.'}), 409
        
    new_user = {
        'email': email,
        'password': password,
        # --- NEW FIELD ---
        'role': role  
    }
    
    users.append(new_user)
    save_users(users)
    
    return jsonify({'success': True, 'message': f'Account for {email} ({role}) created successfully!'})

@app.route('/sign_in', methods=['POST'])
def sign_in():
    """Handles the user sign-in process."""
    email = request.form.get('email')
    password = request.form.get('password')
    users = load_users()

    match = next((user for user in users if user['email'] == email), None)
    
    if match and match['password'] == password:
        # Pass the user's role to the home page route
        home_url = url_for('home', user_email=email, user_role=match['role'])
        return jsonify({'success': True, 'redirect': home_url, 'message': f'Sign In Successful! Redirecting...'})
    else:
        return jsonify({'success': False, 'message': 'Invalid email or password.'}), 401

@app.route('/home')
def home():
    """The new protected home page, now displaying the user's role."""
    user_email = request.args.get('user_email', 'Guest')
    # --- NEW: Get the user's role from the query string ---
    user_role = request.args.get('user_role', 'Unknown')
    return render_template('home.html', user_email=user_email, user_role=user_role)

@app.route('/job_search', methods=['POST'])
def job_search():
    """Handles the job search request by calling the service's job_search method."""
    email = request.form.get('email')
    
    if not email:
        return jsonify({'success': False, 'message': 'Email is required.'}), 400
    
    try:
        # Call the service's job_search method
        results = services.job_search(email)
        return jsonify({'success': True, 'message': 'Job search completed successfully!', 'results': results})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error during job search: {str(e)}'}), 500

if __name__ == '__main__':
    if not os.path.exists(JSON_FILE):
        save_users([])

    app.run(debug=True)
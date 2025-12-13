from flask import Flask, render_template, request, jsonify
import json
import os

# --- Configuration ---
app = Flask(__name__)
JSON_FILE = 'data.json'

# --- JSON Utility Functions ---

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
    """Handles the account creation (Sign Up) process."""
    email = request.form.get('email')
    password = request.form.get('password')
    users = load_users()

    if not email or not password:
        return jsonify({'success': False, 'message': 'Email and Password are required.'}), 400

    # Check if user already exists
    if any(user['email'] == email for user in users):
        return jsonify({'success': False, 'message': 'Account already exists with this email.'}), 409
        
    # --- DANGER: Storing password in plain text ---
    new_user = {
        'email': email,
        'password': password  
    }
    
    users.append(new_user)
    save_users(users)
    
    return jsonify({'success': True, 'message': f'Account for {email} created successfully!'})

@app.route('/sign_in', methods=['POST'])
def sign_in():
    """Handles the user sign-in process."""
    email = request.form.get('email')
    password = request.form.get('password')
    users = load_users()

    # Search for a matching user by email
    match = next((user for user in users if user['email'] == email), None)
    
    if match:
        # --- DANGER: Comparing plain text password ---
        if match['password'] == password:
            return jsonify({'success': True, 'message': f'Sign In Successful! Welcome, {email}.'})
        else:
            # Generic error message for security
            return jsonify({'success': False, 'message': 'Invalid email or password.'}), 401
    else:
        # Generic error message for security
        return jsonify({'success': False, 'message': 'Invalid email or password.'}), 401

if __name__ == '__main__':
    if not os.path.exists(JSON_FILE):
        save_users([])
        
    # Running in debug mode for development
    app.run(debug=True)
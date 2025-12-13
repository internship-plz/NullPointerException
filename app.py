from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os

app = Flask(__name__)

JSON_FILE = 'data.json'

def load_users():
    """Loads existing user data from the JSON file."""
    if not os.path.exists(JSON_FILE):
        return []
    with open(JSON_FILE, 'r') as f:
        try:
            # The JSON file will now store a list of user objects
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_users(users):
    """Writes user data back to the JSON file."""
    with open(JSON_FILE, 'w') as f:
        # Use indent=4 for human-readable formatting
        json.dump(users, f, indent=4)

@app.route('/')
def index():
    """Renders the main login/signup page."""
    users = load_users()
    # Pass the list of existing user emails to the template for display
    user_emails = [user['email'] for user in users]
    return render_template('index.html', user_emails=user_emails)

@app.route('/create_user', methods=['POST'])
def create_user():
    """Handles the user creation (Sign Up) process."""
    email = request.form.get('email')
    password = request.form.get('password')
    
    users = load_users()
    
    # 1. Check if user already exists
    if any(user['email'] == email for user in users):
        return jsonify({'success': False, 'message': 'Account already exists with this email.'}), 409 # Conflict
        
    # 2. Validate input
    if not email or not password:
        return jsonify({'success': False, 'message': 'Email and Password are required.'}), 400 # Bad Request

    # 3. Create new user entry (INSECURE: Password stored in plain text)
    new_user = {
        'email': email,
        'password': password 
    }
    
    users.append(new_user)
    save_users(users)
    
    return jsonify({'success': True, 'message': f'User {email} created successfully. You can now sign in!'})

@app.route('/sign_in', methods=['POST'])
def sign_in():
    """Handles the user sign-in process."""
    email = request.form.get('email')
    password = request.form.get('password')
    
    users = load_users()
    
    # 1. Search for a matching user
    match = next((user for user in users if user['email'] == email), None)
    
    if match:
        # 2. Check password (INSECURE: Plain text comparison)
        if match['password'] == password:
            return jsonify({'success': True, 'message': f'Sign In Successful! Welcome, {email}.'})
        else:
            return jsonify({'success': False, 'message': 'Incorrect Password.'}), 401 # Unauthorized
    else:
        return jsonify({'success': False, 'message': 'User not found. Please create an account.'}), 404 # Not Found

if __name__ == '__main__':
    # Initialize the JSON file if it doesn't exist
    if not os.path.exists(JSON_FILE):
        save_users([])
        
    # The default host is 127.0.0.1 (localhost)
    app.run(debug=True)
from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os
from services.service import Service

# --- Configuration ---
app = Flask(__name__)
JSON_FILE = 'data/users.json'

services = Service()

# --- JSON Utility Functions (Unchanged) ---
def load_users():
    """Loads existing user data from the JSON file."""
    if not os.path.exists(JSON_FILE):
        return []
    try:
        with open(JSON_FILE, 'r') as f:
            data = json.load(f)

        # If file stores a dict mapping email -> userinfo, convert to list
        if isinstance(data, dict):
            users_list = []
            for email, info in data.items():
                if isinstance(info, dict):
                    u = { 'email': email }
                    u.update(info)
                    users_list.append(u)
            return users_list

        # If it's already a list, return as-is
        if isinstance(data, list):
            return data

        return []
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_users(users):
    """Writes user data back to the JSON file."""
    # Persist as a dict mapping email -> userinfo (compat with other modules)
    data_to_write = {}
    if isinstance(users, dict):
        data_to_write = users
    elif isinstance(users, list):
        for u in users:
            if isinstance(u, dict) and 'email' in u:
                entry = { k: v for k, v in u.items() if k != 'email' }
                data_to_write[u['email']] = entry
    else:
        data_to_write = {}

    with open(JSON_FILE, 'w') as f:
        json.dump(data_to_write, f, indent=4)

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
        return jsonify({'success': False, 'message': 'Email, Password, and Role are required.'}), 400

    norm_email = email.strip().lower()
    if any(user.get('email', '').strip().lower() == norm_email for user in users):
        return jsonify({'success': False, 'message': 'Account already exists with this email.'}), 409
    # optional fields: name and skills (skills as "skill:rating, ...")
    name = request.form.get('name', '').strip()
    skills_raw = request.form.get('skills', '').strip()

    skills_dict = {}
    if skills_raw:
        # Try JSON first (the new UI sends skills as JSON string). Fall back to comma-separated pairs.
        try:
            if skills_raw.startswith('{') or skills_raw.startswith('['):
                parsed = json.loads(skills_raw)
                if isinstance(parsed, dict):
                    for k, v in parsed.items():
                        try:
                            skills_dict[k] = int(v)
                        except Exception:
                            try:
                                skills_dict[k] = float(v)
                            except Exception:
                                pass
            else:
                # parse comma-separated pairs like "python:6, javascript:7"
                for part in skills_raw.split(','):
                    if ':' in part:
                        k, v = part.split(':', 1)
                        k = k.strip()
                        try:
                            skills_dict[k] = int(v.strip())
                        except ValueError:
                            try:
                                skills_dict[k] = float(v.strip())
                            except ValueError:
                                # ignore non-numeric values
                                pass
        except json.JSONDecodeError:
            # ignore parse errors and treat as empty
            skills_dict = {}

    new_user = {
        'email': email.strip(),
        'password': password,
        'role': role
    }

    if name:
        new_user['name'] = name
    if skills_dict:
        new_user['skills'] = skills_dict

    users.append(new_user)
    save_users(users)

    return jsonify({'success': True, 'message': f'Account for {email} ({role}) created successfully!'})

@app.route('/sign_in', methods=['POST'])
def sign_in():
    """Handles the user sign-in process."""
    email = request.form.get('email')
    password = request.form.get('password')
    users = load_users()

    norm_email = (email or '').strip().lower()
    match = next((user for user in users if user.get('email', '').strip().lower() == norm_email), None)

    if not match:
        app.logger.debug(f"Sign in failed: no account for email={email}")
        return jsonify({'success': False, 'message': 'No account found for that email.'}), 401

    if match.get('password') != password:
        app.logger.debug(f"Sign in failed: incorrect password for email={email}")
        return jsonify({'success': False, 'message': 'Incorrect password.'}), 401

    home_url = url_for('home', user_email=match.get('email'), user_role=match.get('role', 'Unknown'))
    return jsonify({'success': True, 'redirect': home_url, 'message': f'Sign In Successful! Redirecting...'})

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
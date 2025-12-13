from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

JSON_FILE = 'data.json'

def load_data():
    """Loads existing data from the JSON file."""
    if not os.path.exists(JSON_FILE):
        return []
    with open(JSON_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            # Handle empty or invalid JSON file
            return []

def save_data(data):
    """Writes data back to the JSON file."""
    with open(JSON_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def index():
    """Renders the main page and displays current click history."""
    history = load_data()
    return render_template('index.html', history=history)

@app.route('/click', methods=['POST'])
def record_click():
    """Records a button click event."""
    button_name = request.form.get('button_name', 'Unknown Button')
    
    new_entry = {
        'button': button_name,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'message': f"Button '{button_name}' was clicked."
    }
    
    data = load_data()
    data.append(new_entry)
    save_data(data)
    
    # Return the new entry as JSON for the client-side update
    return jsonify(new_entry)

if __name__ == '__main__':
    # Initialize the JSON file if it doesn't exist
    if not os.path.exists(JSON_FILE):
        save_data([])
        
    app.run(debug=True)
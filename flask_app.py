from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from functions.bitbucket_restapi import create_pull_request, get_workspace_members
from pymongo import MongoClient
import os
import certifi

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for session and flash messages

# MongoDB Atlas setup
MONGO_URI = os.getenv('MONGO_URI', 'mongodb+srv://username:password@ac-8fqyk8w-shard-00-00.4sximek.mongodb.net/?retryWrites=true&w=majority')
DB_NAME = os.getenv('DB_NAME', 'jugaad_ai')
COLLECTION_NAME = 'users'

def get_db():
    # Use certifi for SSL certificate verification and enable TLS
    client = MongoClient(
        MONGO_URI,
        tls=True,
        tlsCAFile=certifi.where()
    )
    return client[DB_NAME]

def load_settings():
    try:
        db = get_db()
        username = os.getenv('BITBUCKET_USERNAME')
        if not username:
            return {}
        settings = db[COLLECTION_NAME].find_one({'username': username})
        if settings:
            # Remove MongoDB's _id field from the settings
            settings.pop('_id', None)
            return settings
    except Exception as e:
        print(f"Error loading settings from MongoDB: {str(e)}")
    return {}

def save_settings_to_db(settings):
    try:
        db = get_db()
        username = settings.get('BITBUCKET_USERNAME')
        if not username:
            return False
            
        # Use username as the primary key for upsert
        db[COLLECTION_NAME].update_one(
            {'username': username},
            {'$set': settings},
            upsert=True
        )
        return True
    except Exception as e:
        print(f"Error saving settings to MongoDB: {str(e)}")
        return False

def update_environment_variables(settings):
    for key, value in settings.items():
        os.environ[key] = value

@app.route("/", methods=['GET'])
def index():
    settings = load_settings()
    if not all(key in settings for key in ['BITBUCKET_USERNAME', 'BITBUCKET_APP_PASSWORD', 'WORKSPACE', 'REPO_SLUG']):
        flash('Please configure your Bitbucket settings first', 'error')
        return redirect(url_for('settings'))
    
    try:
        workspace_members = get_workspace_members()
        return render_template('index.html', workspace_members=workspace_members)
    except Exception as e:
        flash('Error fetching workspace members. Please check your settings.', 'error')
        return redirect(url_for('settings'))

@app.route("/settings", methods=['GET'])
def settings():
    current_settings = load_settings()
    return render_template('settings.html', settings=current_settings)

@app.route("/save_settings", methods=['POST'])
def save_settings():
    new_settings = {
        'BITBUCKET_USERNAME': request.form.get('username'),
        'BITBUCKET_APP_PASSWORD': request.form.get('access_token'),
        'WORKSPACE': request.form.get('workspace'),
        'REPO_SLUG': request.form.get('repo_slug')
    }
    
    # Validate that all fields are provided
    if not all(new_settings.values()):
        flash('All fields are required', 'error')
        return redirect(url_for('settings'))
    
    try:
        if save_settings_to_db(new_settings):
            update_environment_variables(new_settings)
            flash('Settings saved successfully', 'success')
            return redirect(url_for('index'))
        else:
            flash('Error saving settings to database', 'error')
            return redirect(url_for('settings'))
    except Exception as e:
        flash(f'Error saving settings: {str(e)}', 'error')
        return redirect(url_for('settings'))

@app.route("/create_pr", methods=['POST'])
def create_pr():
    try:
        input_text = request.json.get("input_text")
        reviewer_uuids = request.json.get("reviewer_uuids", [])
        
        if not input_text:
            return jsonify({"error": "No input text provided"}), 400

        result = create_pull_request(input_text, reviewer_uuids)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Load settings at startup
    settings = load_settings()
    if settings:
        update_environment_variables(settings)
    app.run(debug=True)

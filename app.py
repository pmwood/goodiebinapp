from flask import Flask, render_template, request, redirect, url_for, session
from azure.storage.blob import BlobServiceClient
import os
import msal
from flask_session import Session

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Load configuration from config.py
app.config.from_object('config')

# Initialize BlobServiceClient
blob_service_client = BlobServiceClient.from_connection_string(app.config['AZURE_STORAGE_CONNECTION_STRING'])
container_name = app.config['AZURE_CONTAINER_NAME']

# Initialize Flask-Session
app.config['SESSION_TYPE'] = app.config['SESSION_TYPE']
Session(app)

# MSAL setup
def _build_msal_app(cache=None):
    return msal.ConfidentialClientApplication(
        app.config['CLIENT_ID'], authority=app.config['AUTHORITY'],
        client_credential=app.config['CLIENT_SECRET'], token_cache=cache)

def _build_auth_url():
    return _build_msal_app().get_authorization_request_url(
        app.config['SCOPE'], redirect_uri=url_for('authorized', _external=True))

@app.route('/')
def index():
    if not session.get('user'):
        return redirect(url_for('login'))
    # List blobs in the container
    container_client = blob_service_client.get_container_client(container_name)
    blob_list = container_client.list_blobs()
    return render_template('index.html', blobs=blob_list, user=session['user'])

@app.route('/upload', methods=['POST'])
def upload():
    if not session.get('user'):
        return redirect(url_for('login'))
    file = request.files['file']
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=file.filename)
    blob_client.upload_blob(file)
    return redirect(url_for('index'))

@app.route('/download/<blob_name>')
def download(blob_name):
    if not session.get('user'):
        return redirect(url_for('login'))
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    download_stream = blob_client.download_blob()
    return download_stream.readall()

@app.route('/login')
def login():
    auth_url = _build_auth_url()
    return redirect(auth_url)

@app.route(app.config['REDIRECT_PATH'])
def authorized():
    cache = msal.SerializableTokenCache()
    if request.args.get('state'):
        result = _build_msal_app(cache).acquire_token_by_authorization_code(
            request.args['code'],
            scopes=app.config['SCOPE'],
            redirect_uri=url_for('authorized', _external=True))
        if 'error' in result:
            return "Login failure: " + result['error_description']
        session['user'] = result.get('id_token_claims')
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(
        app.config['AUTHORITY'] + "/oauth2/v2.0/logout" +
        "?post_logout_redirect_uri=" + url_for('index', _external=True))

if __name__ == '__main__':
    app.run(debug=True)

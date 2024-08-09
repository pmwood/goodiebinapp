from flask import Flask, render_template, request, redirect, url_for
from azure.storage.blob import BlobServiceClient
import os

app = Flask(__name__)

# Load configuration from config.py
app.config.from_object('config')

# Initialize BlobServiceClient
blob_service_client = BlobServiceClient.from_connection_string(app.config['AZURE_STORAGE_CONNECTION_STRING'])
container_name = app.config['AZURE_CONTAINER_NAME']

@app.route('/')
def index():
    # List blobs in the container
    container_client = blob_service_client.get_container_client(container_name)
    blob_list = container_client.list_blobs()
    return render_template('index.html', blobs=blob_list)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=file.filename)
    blob_client.upload_blob(file)
    return redirect(url_for('index'))

@app.route('/download/<blob_name>')
def download(blob_name):
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    download_stream = blob_client.download_blob()
    return download_stream.readall()

if __name__ == '__main__':
    app.run(debug=True)

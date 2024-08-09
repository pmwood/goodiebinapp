import os

AZURE_STORAGE_CONNECTION_STRING = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
AZURE_CONTAINER_NAME = os.getenv('AZURE_CONTAINER_NAME')

# Entra ID configuration
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
AUTHORITY = os.getenv('AUTHORITY')  # e.g., 'https://login.microsoftonline.com/your_tenant_id'
REDIRECT_PATH = os.getenv('REDIRECT_PATH')  # e.g., '/getAToken'
SCOPE = ["User.Read"]
SESSION_TYPE = "filesystem"

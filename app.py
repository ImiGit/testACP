from flask import Flask, render_template, request, redirect, url_for, session
import jwt
import pyodbc
import os
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
import requests, base64 , secrets

# Load environment variables from a .env file
from dotenv import load_dotenv
load_dotenv()

connection_string_storage = os.getenv('AZURE_STORAGE_CONNECTION_STRING')

server = os.getenv('AZURE_SQL_SERVER')
port = os.getenv('AZURE_SQL_PORT')
database = os.getenv('AZURE_SQL_DATABASE')
authentication = os.getenv('AZURE_SQL_AUTHENTICATION')

# Replace 'your_storage_account_url' with the actual URL of your Azure Storage account
account_url = 'https://imistorage2.blob.core.windows.net/'

# Create an instance of DefaultAzureCredential
default_credential = DefaultAzureCredential()

# Create a BlobServiceClient using the DefaultAzureCredential
client = BlobServiceClient(account_url, credential=default_credential)

# Uncomment the following lines according to the authentication type.
# For system-assigned managed identity.
connection_string_sql = f'Driver={{ODBC Driver 18 for SQL Server}};Server={server},{port};Database={database};Authentication={authentication};Encrypt=yes;'


app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16) 
app.config['SESSION_TYPE'] = 'filesystem'

# Microsoft Graph API endpoint to fetch user information
GRAPH_ENDPOINT = 'https://graph.microsoft.com/v1.0/me'

def get_blob_service_client():
    # Replace with your Azure Storage account connection string
    #return BlobServiceClient.from_connection_string(connection_string_storage)
    return BlobServiceClient(account_url, credential=default_credential)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            return redirect(request.url)

        blob_service_client = get_blob_service_client()

        # Get selected container name from the form
        container_name = request.form.get('container_name')

        # Use the selected container directly
        container_client = blob_service_client.get_container_client(container_name)

        # Save the uploaded file to Azure Blob Storage
        blob_client = container_client.get_blob_client(file.filename)
        with file.stream as data:
            blob_client.upload_blob(data)

        # Redirect to a success page or display a success message
        return redirect(url_for('success'))

    # List all containers
    blob_service_client = get_blob_service_client()
    containers = [container.name for container in blob_service_client.list_containers()]

    #TODO: List all blobs in each container
    # List all blobs in the container
    # blobs = blob_service_client.list_blobs()
    # blob_info = [(blob.name, blob.creation_time, blob.size, blob.container) for blob in blobs]

    return render_template('home.html', containers=containers, existing_containers=containers)

@app.route('/success')
def success():
    # You can customize this page to display a success message
    return f"File uploaded successfully! <a href='{url_for('home')}'>Go back to home</a>"

@app.route('/sql')
def sql():
    # Connect to the database
    connection = pyodbc.connect(connection_string_sql)

    # Create a cursor from the connection
    cursor = connection.cursor()

    # Execute a simple query to fetch user data
    cursor.execute('SELECT * FROM Persons')

    # Fetch all rows
    persons = cursor.fetchall()

    # Close the cursor and connection
    cursor.close()
    connection.close()

    return render_template('sql.html', persons=persons)


@app.route('/userInfo')
def userInfo():
    response='123'
    response2='!!'
    if request.headers.get('X-MS-TOKEN-AAD-ACCESS-TOKEN', 'NA') != 'NA':
        id_token = request.headers.get('X-MS-TOKEN-AAD-ID-TOKEN')
        accessToken = request.headers.get('X-MS-TOKEN-AAD-ACCESS-TOKEN')

        remote_url = 'https://graph.microsoft.com/v1.0/me'
        headers2 = {'Authorization': f'Bearer {accessToken}'}
        response2 = requests.get(remote_url, headers=headers2)

        username = ''
        email = ''
        if response2.ok:
            # Extract display name from JSON response
            profile_data = response2.json().get('displayName')
            username = 'done'
            email = profile_data

        graph_api_url = 'https://graph.microsoft.com/v1.0/me/photo/$value'
        response = requests.get(graph_api_url, headers={'Authorization': 'Bearer ' + accessToken})

        profile_picture_url = ''
        if response.status_code == 200:
            profile_picture_url = 'data:image/jpeg;base64,' + base64.b64encode(response.content).decode('utf-8')

        return render_template('userInfo.html', username=username, email=email, profile_picture=profile_picture_url)

    return render_template('userInfo.html', access_token=request.headers.get('X-MS-TOKEN-AAD-ACCESS-TOKEN', 'NA'),
                           id_token=request.headers.get('X-MS-TOKEN-AAD-ID-TOKEN', 'NA'), response1=response, response2=response2)


""" @app.route('/userInfo')
def userInfo():

    if request.headers.get('x-ms-token-aad-access-token','NA') != 'NA': #request.headers.get('x-ms-token-aad-access-token') is not None:
        id_token = request.headers.get('X-MS-TOKEN-AAD-ID-TOKEN')
        #decoded_token = jwt.decode(id_token, verify=False)

        accessToken = request.headers.get('x-ms-token-aad-access-token')

        remote_url  = 'https://graph.microsoft.com/v1.0/me'
        headers2 = {'Authorization': f'Bearer {accessToken}'}
        response2 = requests.get(remote_url, headers=headers2)

        username = ''
        email = ''
        if response2.ok:
            # Extract profile from JSON response
            profile_data = response.json().get('profile')
            username='done'
            email=profile_data

        # Assuming 'access_token' is the access token obtained during authentication
        graph_api_url = 'https://graph.microsoft.com/v1.0/me/photo/$value'
        response = requests.get(graph_api_url, headers={'Authorization': 'Bearer ' + accessToken})

        profile_picture_url = ''
        if response.status_code == 200:
            profile_picture_url = 'data:image/jpeg;base64,' + base64.b64encode(response.content).decode('utf-8')

        # Extract user information from the decoded token
        #username = decoded_token.get('preferred_username', 'N/A')
        #email = decoded_token.get('email', 'N/A')
        #profile_picture = decoded_token.get('picture', 'N/A')

        return render_template('userInfo.html', username=username, email=email, profile_picture=profile_picture_url)
    
    return render_template('userInfo.html', session=session, acces_token=request.headers.get('x-ms-token-aad-access-token','NA'),
                           id_token=request.headers.get('X-MS-TOKEN-AAD-ID-TOKEN', 'NA'), response1=response, response2=response2)
 """
if __name__ == '__main__':
    app.run(debug=True)
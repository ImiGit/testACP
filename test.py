"""import pyodbc
from azure.identity import DefaultAzureCredential

# Specify your database information
database_server = "imi_server"
database_name = "sqlDB"

# Step 1: Instantiate DefaultAzureCredential (no need to specify client_id when using managed identity)
credential = DefaultAzureCredential()

# Step 2: Get an Access Token
token = credential.get_token(f"https://{database_server}.database.windows.net")

# Step 3: Construct the Connection String with the Access Token
connection_string = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={database_server}.database.windows.net;"
    f"DATABASE={database_name};"
    f"Authentication=ActiveDirectoryMSI;"
    f"AccessToken={token.token}"
)

print(connection_string)

# Step 4: Open the Connection
conn = pyodbc.connect(connection_string)
cursor = conn.cursor()

# Now you can use the cursor to execute SQL queries or perform database operations

# Don't forget to close the connection when done
conn.close()"""
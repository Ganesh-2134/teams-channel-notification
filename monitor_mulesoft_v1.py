import requests
from tabulate import tabulate
import boto3
import json
from datetime import datetime
from botocore.exceptions import NoCredentialsError


# Create a session with the specified profile
profile_name = 'hvcpnonprod'
region_name = 'eu-west-1'

# Set your MuleSoft url and list of environments
MULESOFT = "https://anypoint.mulesoft.com"
ENVIRONMENTS = ["SIT", "E2ETT","UAT","UATTT","E2E","NFT-TEST"]


def get_secret(secret_name):
    session = boto3.Session(profile_name=profile_name)
    client = session.client(service_name='secretsmanager', region_name=region_name)

    try:
        response = client.get_secret_value(SecretId=secret_name)
        secret_string = response['SecretString']
        return secret_string
    except NoCredentialsError:
        print("Credentials not available.")
    except Exception as e:
        print(f"Error retrieving secret: {str(e)}")



# Function to obtain an access token
def get_access_token(username, password):
    login_data = {"username": username, "password": password}
    token_response = requests.post(f"{MULESOFT}/accounts/login", json=login_data)
    return token_response.json()["access_token"]

# Function to get the organization ID
def get_organization_id(access_token):
    org_id_response = requests.get(f"{MULESOFT}/accounts/api/me", headers={"Authorization": f"Bearer {access_token}"})
    return org_id_response.json()["user"]["contributorOfOrganizations"][0]["id"]

# Function to get the environment ID
def get_environment_id(access_token, org_id, env_name):
    env_id_response = requests.get(f"{MULESOFT}/accounts/api/organizations/{org_id}/environments", headers={"Authorization": f"Bearer {access_token}"})
    return next((env["id"] for env in env_id_response.json()["data"] if env["name"] == env_name), None)

# Function to get applications
def get_applications(access_token, org_id, env_id):
    applications_response = requests.get(
        f"{MULESOFT}/hybrid/api/v1/applications",
        headers={"Authorization": f"Bearer {access_token}", "X-ANYPNT-ENV-ID": str(env_id), "X-ANYPNT-ORG-ID": str(org_id)},
    )
    return applications_response.json()["data"]

# Function to get servers
def get_servers(access_token, org_id, env_id):
    server_api_url = f"{MULESOFT}/hybrid/api/v1/servers"
    server_response = requests.get(
        server_api_url,
        headers={"Authorization": f"Bearer {access_token}", "X-ANYPNT-ENV-ID": str(env_id), "X-ANYPNT-ORG-ID": str(org_id)},
    )
    return server_response.json().get("data", [])

# Function to filter applications by status
def filter_applications_by_status(applications, status):
    return [app for app in applications if app["lastReportedStatus"] != status]

# Function to filter servers by status
def filter_servers_by_status(servers, status):
    return [server for server in servers if server["status"] != status]

# Function to print tabular data
def print_tabular_data(data):
    print(tabulate(data, headers="keys", tablefmt="grid"))

def convert_epoch_to_datetime(epoch_time_milliseconds):
    # Convert milliseconds to seconds
    epoch_time_seconds = epoch_time_milliseconds / 1000.0
    
    # Convert epoch time to a human-readable format
    formatted_time = datetime.utcfromtimestamp(epoch_time_seconds).strftime('%Y-%m-%d %H:%M:%S UTC')
    
    return formatted_time

# Function to collect environment data
def collect_environment_data(username, password, env_name):
    # Obtain an access token
    access_token = get_access_token(username, password)

    # Get the organization ID
    org_id = get_organization_id(access_token)

    # Get the environment ID
    env_id = get_environment_id(access_token, org_id, env_name)

    # Get applications
    applications = get_applications(access_token, org_id, env_id)

    # Get servers
    servers = get_servers(access_token, org_id, env_id)

    # Filter applications and servers by status
    filtered_applications = filter_applications_by_status(applications, 'STARTED')
    filtered_servers = filter_servers_by_status(servers, 'RUNNING')

    # Collect data for the environment
    app_data = []
    server_data = []

    # Add application data
    for app in filtered_applications:
        date_modified = convert_epoch_to_datetime(app['timeUpdated'])
        app_data.append({"Environment": env_name, "Application": app["name"], "Status": app["lastReportedStatus"], "Date Modified": date_modified})

    # Add server data
    for server in filtered_servers:
        server_data.append({"Environment": env_name, "Server": server["name"], "Status": server["status"]})

    return app_data, server_data


secret_name = 'hvcp.automation.mulesoft'
secret_data = get_secret(secret_name)
secret_json = json.loads(secret_data)

# Extract username and password
MUSER = secret_json.get("user")
MPASS = secret_json.get("pass")

# Collect data for all environments
all_app_data = []
all_server_data = []

for env in ENVIRONMENTS:
    app_data, server_data = collect_environment_data(MUSER, MPASS, env)
    all_app_data.extend(app_data)
    all_server_data.extend(server_data)

# Print the final tabular data
print("\nFinal Report:")
print("Applications not in 'STARTED' status:")
if all_app_data:
    print_tabular_data(all_app_data)
else:
    print("None")

print("\n\nServers not in 'RUNNING' status:")
if all_server_data:
    print_tabular_data(all_server_data)
else:
    print("None\n")
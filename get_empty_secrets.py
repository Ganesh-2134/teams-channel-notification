import boto3
import json
from openpyxl import Workbook

# Create a session with the specified profile
profile_name = 'hvcptest'
region_name = 'eu-west-1'

session = boto3.Session(profile_name=profile_name)
client = session.client(service_name='secretsmanager', region_name=region_name)

def list_all_secrets():
    # Initialize the Secrets Manager client

    all_secrets = []
    next_token = None

    # Retrieve all secrets using pagination
    while True:
        # List secrets with optional NextToken
        if next_token:
            response = client.list_secrets(NextToken=next_token)
        else:
            response = client.list_secrets()

        # Append the secrets to the list
        all_secrets.extend(response['SecretList'])

        # Check if there are more secrets to fetch
        if 'NextToken' in response:
            next_token = response['NextToken']
        else:
            break

    return all_secrets

def check_secrets_for_empty_and_key_values():
    # Retrieve all secrets
    all_secrets = list_all_secrets()

    # Initialize empty lists to store results
    empty_secrets = []
    matched_secrets = []

    # Check each secret's value and specified key-value pairs
    for secret in all_secrets:
        secret_name = secret['Name']
        if 'e2ecv' not in secret_name:
            continue
        
        # Retrieve the secret value
        try:
            get_secret_value_response = client.get_secret_value(SecretId=secret_name)
            secret_value = get_secret_value_response.get('SecretString', '')

            # Check if the value is empty
            if not secret_value:
                empty_secrets.append(secret_name)
            else:
                try:
                    # Check if the secret contains the specified key-value pairs
                    secret_value = json.loads(secret_value)
                    if isinstance(secret_value, list):
                        secret_value = secret_value[0]
                    if 'username' in secret_value.keys() and 'password' in secret_value.keys():
                        if secret_value['username'] == 'username' and secret_value['password'] == 'password':
                            matched_secrets.append(secret_name)
                except json.JSONDecodeError:
                    # Handle JSON formatting issues
                    print(f"JSON formatting issue for secret: {secret_name}")
                    empty_secrets.append(secret_name)
        except client.exceptions.ResourceNotFoundException:
            empty_secrets.append(secret_name)

    return empty_secrets, matched_secrets

# Call the function to check for empty secrets and specified key-value pairs
empty_secrets, matched_secrets = check_secrets_for_empty_and_key_values()

# Writing results to an Excel file
wb = Workbook()
ws = wb.active

# Write headers
ws.append(["Secrets with empty values:"])
for secret_name in empty_secrets:
    ws.append([secret_name])

ws.append([])  # add an empty row for spacing

ws.append(["Secrets matching specified key-value pairs:"])
for secret_name in matched_secrets:
    ws.append([secret_name])

# Save the Excel file
wb.save("secrets_report1.xlsx")

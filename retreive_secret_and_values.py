import boto3
import pandas as pd
from botocore.exceptions import ClientError

def get_all_secrets(profile_name, region_name):
    session = boto3.Session(profile_name=profile_name, region_name=region_name)
    client = session.client('secretsmanager')

    # Retrieve all secret IDs
    paginator = client.get_paginator('list_secrets')
    secrets = []
    for page in paginator.paginate():
        for secret in page['SecretList']:
            if 'trn' in secret['Name'] or 'trn.' in secret['Name']:
                secrets.append(secret['Name'])

    # Retrieve secret values
    secret_data = {}
    for secret_name in secrets:
        try:
            secret_value = client.get_secret_value(SecretId=secret_name)
            secret_data[secret_name] = secret_value['SecretString']
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print(f"Secret '{secret_name}' not found. Skipping...")
            else:
                print(f"Error retrieving secret '{secret_name}': {e}")

    return secret_data

def save_to_excel(secret_data, excel_file):
    df = pd.DataFrame(secret_data.items(), columns=['SecretName', 'SecretValue'])
    df.to_excel(excel_file, index=False)

if __name__ == "__main__":
    profile_name = 'hvcptest'
    region_name = 'eu-west-1'
    excel_file = 'trn_latest_secrets_with_values.xlsx'

    secrets = get_all_secrets(profile_name, region_name)
    save_to_excel(secrets, excel_file)

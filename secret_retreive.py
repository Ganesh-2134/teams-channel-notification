import boto3
import pandas as pd

def get_specific_secret_names(profile_name, region_name, prefixes):
    session = boto3.Session(profile_name=profile_name, region_name=region_name)
    client = session.client('secretsmanager')

    # Retrieve all secret IDs
    paginator = client.get_paginator('list_secrets')
    secret_names = {prefix: [] for prefix in prefixes}  # Initialize dictionary with empty lists for each prefix
    for page in paginator.paginate():
        for secret in page['SecretList']:
            for prefix in prefixes:
                if secret['Name'].startswith(prefix):
                    secret_names[prefix].append(secret['Name'])

    return secret_names

def save_to_excel(secret_names, excel_file):
    with pd.ExcelWriter(excel_file) as writer:
        for prefix, names in secret_names.items():
            df = pd.DataFrame(names, columns=['SecretName'])
            df.to_excel(writer, sheet_name=prefix, index=False)

if __name__ == "__main__":
    profile_name = 'hvcptest'
    region_name = 'eu-west-1'
    excel_file = 'filtered_secret_namess.xlsx'
    prefixes = ['e2ecv', 'nft', 'nfttest', 'uat']

    secret_names = get_specific_secret_names(profile_name, region_name, prefixes)
    save_to_excel(secret_names, excel_file)

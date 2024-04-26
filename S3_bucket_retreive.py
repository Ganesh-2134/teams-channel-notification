import boto3
import pandas as pd
from botocore.exceptions import ClientError

def get_all_s3_buckets(profile_name, region_name):
    session = boto3.Session(profile_name=profile_name, region_name=region_name)
    s3_client = session.client('s3')

    try:
        response = s3_client.list_buckets()
        bucket_names = [bucket['Name'] for bucket in response['Buckets'] if 'e2e-' in bucket['Name']]
        #bucket_names = [bucket['Name'] for bucket in response['Buckets'] if 'uattt' in bucket['Name'] and 'uat' not in bucket['Name']]
        print("Found S3 buckets:", bucket_names)  # Debugging statement
        return bucket_names
    except ClientError as e:
        print(f"Error retrieving S3 buckets: {e}")
        return []
#dev, sit, uat, uattt, e2ett
def save_to_excel(bucket_names, excel_file):
    df = pd.DataFrame(bucket_names, columns=['BucketName'])
    df.to_excel(excel_file, index=False)

if __name__ == "__main__":
    profile_name = 'hvcpnonprod'
    region_name = 'eu-west-1'
    excel_file = 's3_buckets_all.xlsx'

    buckets = get_all_s3_buckets(profile_name, region_name)
    print("Number of buckets:", len(buckets))  # Debugging statement
    save_to_excel(buckets, excel_file)

import boto3
import pandas as pd
from botocore.exceptions import ClientError

def get_ec2_instance_tags(profile_name, region_name, instance_id):
    session = boto3.Session(profile_name=profile_name, region_name=region_name)
    ec2_client = session.client('ec2')

    try:
        response = ec2_client.describe_tags(
            Filters=[
                {
                    'Name': 'resource-id',
                    'Values': [instance_id]
                }
            ]
        )
        tags = {tag['Key']: tag['Value'] for tag in response['Tags']}
        print("Tags for EC2 instance:", tags)  # Debugging statement
        return tags
    except ClientError as e:
        print(f"Error retrieving EC2 instance tags: {e}")
        return {}

def save_to_excel(tags, excel_file):
    df = pd.DataFrame(list(tags.items()), columns=['Key', 'Value'])
    df.to_excel(excel_file, index=False)

if __name__ == "__main__":
    profile_name = 'hvcpnonprod'
    region_name = 'eu-west-1'
    excel_file = 'ec2_instance_tags.xlsx'
    instance_id = 'i-03d0774bfd84b02a2'

    instance_tags = get_ec2_instance_tags(profile_name, region_name, instance_id)
    print("Number of tags:", len(instance_tags))  # Debugging statement
    save_to_excel(instance_tags, excel_file)

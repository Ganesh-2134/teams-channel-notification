import boto3
import time
import re
import pandas as pd

timestr = time.strftime("%Y%m%d_%H%M%S")

# Replace 'your_profile_name' with the name of your AWS profile
profile_name = 'motdev'
#profile_name = 'hvcpnonprod'
#profile_name = 'supportradar'
 
command_id = 'efacc7d0-8516-4565-b5f4-1a507ce9d906'

# command_to_execute = f"sudo cat /etc/sysconfig/guidewire-*-${{HOSTNAME}} | grep \"$JAVA_OPTS -Xms\""
ssm_document_name = 'mot-retieve-host-name'
command_to_execute = ""

# Define the tag keys and values to filter instances.
custom_filter = [
    # {
    #     'Name': 'tag:environment',
    #     'Values': ['Prod']
    # },
    {
        'Name': 'instance-state-name',
        'Values': ['running']
    },
    {
        'Name': 'tag:os',
        'Values': ['windows']
    },
    {
        'Name': 'tag:project',
        'Values': ['mot']
    },
]

region_name = 'eu-west-1'

# Create a session with the specified profile
session = boto3.Session(profile_name=profile_name)
ec2_client = session.client('ec2', region_name=region_name)
ssm_client = session.client('ssm', region_name=region_name)

def format_output(content):
    # Split the content into lines
    lines = content.split('\n')

    # Define a regular expression pattern to capture the offset value
    pattern = r'offset ([-+]?[0-9]+\.[0-9]+)'

    # Iterate through the lines and extract offset values from lines containing "ntpdate"
    offset_values = []
    for line in lines:
        if "ntpdate" in line:
            offset_match = re.search(pattern, line)
            if offset_match:
                offset_values.append(offset_match.group(1))

    # Print the extracted offset values
    return offset_values[0]

def get_instance_ids(filters):
    instance_ids = []
    next_token = None
    while True:
        if next_token:
            response = ec2_client.describe_instances(Filters=filters, NextToken=next_token)
        else:
            response = ec2_client.describe_instances(Filters=filters)
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instance_ids.append(instance['InstanceId'])
        next_token = response.get('NextToken')
        if not next_token:
            break
    return instance_ids

def run_ssm_command(instance_ids, document_name, command_to_execute):
    command_ids = []
    chunk_size = 50
    for i in range(0, len(instance_ids), chunk_size):
        instance_chunk = instance_ids[i:i + chunk_size]
        response = ssm_client.send_command(
            InstanceIds=instance_chunk,
            DocumentName=document_name,
        )
        command_ids.append(response['Command']['CommandId'])
    return command_ids

def get_command_invocations(command_id):
    cmd_invocations = []
    next_token = None
    while True:
        if next_token:
            response = ssm_client.list_command_invocations(CommandId=command_id, NextToken=next_token)
        else:
            response = ssm_client.list_command_invocations(CommandId=command_id)
        cmd_invocations.extend(response.get('CommandInvocations', []))
        next_token = response.get('NextToken')
        if not next_token:
            break
    return cmd_invocations

def process_instances_1(instance_ids, document_name, command_to_execute):
    # Send SSM command to instances
    command_ids = run_ssm_command(instance_ids, document_name, command_to_execute)
    time.sleep(20)  # Wait for the command to finish

    # Get command invocations using pagination
    cmd_invocations = []
    for command_id in command_ids:
        cmd_invocations.extend(get_command_invocations(command_id))

    # Extract instance information
    instances = [(x['InstanceId'], x['InstanceName']) for x in cmd_invocations]

    # Create an empty list to store rows
    rows = []
    for inst_id, inst_name in instances:
        command_output = ssm_client.get_command_invocation(InstanceId=inst_id,
            CommandId=command_id)['StandardOutputContent']
        # command_output = format_output(command_output)

        # Append the result as a dictionary to the list of rows
        rows.append({'Instance Name': inst_name, 'Command Output': command_output})

    # Create a DataFrame from the list of rows
    results_df = pd.DataFrame(rows)
    return results_df

def process_instances(command_id):
    # Send SSM command to instances
    # command_ids = run_ssm_command(instance_ids, document_name, command_to_execute)
    # time.sleep(20)  # Wait for the command to finish

    # Get command invocations using pagination
    cmd_invocations = []
    cmd_invocations.extend(get_command_invocations(command_id))

    # Extract instance information
    instances = [(x['InstanceId'], x['InstanceName']) for x in cmd_invocations]

    # Create an empty list to store rows
    rows = []
    for inst_id, inst_name in instances:
        command_output = ssm_client.get_command_invocation(InstanceId=inst_id,
            CommandId=command_id)['StandardOutputContent']
        # command_output = format_output(command_output)

        # # Retrieve EC2 instance name tag
        # response = ec2_client.describe_instances(InstanceIds=[inst_id])
        # instance_name = ""
        # for reservation in response['Reservations']:
        #     for instance in reservation['Instances']:
        #         for tag in instance.get('Tags', []):
        #             if tag['Key'] == 'Name':
        #                 instance_name = tag['Value']
        #                 break
        #         if instance_name:
        #             break
        #     if instance_name:
        #         break

        # # Append the result as a dictionary to the list of rows
        # rows.append({'Instance ID': inst_id, 'Instance Name': instance_name, 'Command Output': command_output})
        # Retrieve EC2 instance name and environment tags
        response = ec2_client.describe_instances(InstanceIds=[inst_id])
        instance_name = ""
        environment_tag = ""
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                for tag in instance.get('Tags', []):
                    if tag['Key'] == 'Name':
                        instance_name = tag['Value']
                    elif tag['Key'] == 'environment':
                        environment_tag = tag['Value']
                if instance_name and environment_tag:
                    break
            if instance_name and environment_tag:
                break

        # Append the result as a dictionary to the list of rows
        rows.append({'Instance ID': inst_id, 'Instance Name': instance_name, 'Environment': environment_tag, 'Command Output': command_output})


    # Create a DataFrame from the list of rows
    results_df = pd.DataFrame(rows)
    return results_df

# Get instance IDs using pagination
instance_ids = get_instance_ids(custom_filter)

# Process instances in chunks of 50
# chunk_size = 50
# dfs = []
# for i in range(0, len(instance_ids), chunk_size):
#     instance_chunk = instance_ids[i:i + chunk_size]
dfs = process_instances( command_id)
# dfs.append(df)


# Combine all DataFrames
# combined_df = pd.concat(dfs)
combined_df = dfs

# Specify the Excel file name
excel_file_name = f'output\{ssm_document_name}_results_{timestr}.xlsx'

# Save the DataFrame to an Excel file
combined_df.to_excel(excel_file_name, index=False)

print(f'Results have been saved to {excel_file_name}')

import boto3
from datetime import datetime, timedelta
import pytz
from tabulate import tabulate
from botocore.exceptions import ClientError 



# profile_name = 'cthvcpprod' #hvcptest
# profile_name = 'hvcptest', cthvcpprod, hvcpnonprod

region_name = 'eu-west-1';

all_env = False
lower_env_only = False

def create_client(region_name, service_name, profile_name):
    session = boto3.Session(profile_name=profile_name)
    client = session.client(service_name, region_name=region_name)
    return client

# Define the list of environments, their corresponding pipeline names, and X-Center values
environments = {
    "E2E": [
        {"Pipeline": "hvcp-pc-e2e-build-pipeline", "X-Center": "PC"},
        {"Pipeline": "hvcp-cc-e2e-build-pipeline", "X-Center": "CC"},
        {"Pipeline": "hvcp-cccm-e2e-build-pipeline", "X-Center": "CCCM"},
        {"Pipeline": "hvcp-e2e-pc-release-deploy", "X-Center": "PC"},
        {"Pipeline": "hvcp-e2e-cc-release-deploy", "X-Center": "CC"},
        {"Pipeline": "hvcp-e2e-cccm-release-deploy", "X-Center": "CCCM"},
        {"Pipeline": "hvcp-e2e-mu-master-deploy", "X-Center": "Mule"},
    ],
    "UAT": [
        {"Pipeline": "hvcp-pc-uat-build-pipeline", "X-Center": "PC"},
        {"Pipeline": "hvcp-cc-uat-build-pipeline", "X-Center": "CC"},
        {"Pipeline": "hvcp-cccm-uat-build-pipeline", "X-Center": "CCCM"},
        {"Pipeline": "hvcp-uat-pc-release-deploy", "X-Center": "PC"},
        {"Pipeline": "hvcp-uat-cc-release-deploy", "X-Center": "CC"},
        {"Pipeline": "hvcp-uat-cccm-release-deploy", "X-Center": "CCCM"},
        {"Pipeline": "hvcp-uat-mu-master-deploy", "X-Center": "Mule"},
    ],
    "UATTT": [
        {"Pipeline": "hvcp-pc-uattt-build-pipeline", "X-Center": "PC"},
        {"Pipeline": "hvcp-cc-uattt-build-pipeline", "X-Center": "CC"},
        {"Pipeline": "hvcp-cccm-uattt-build-pipeline", "X-Center": "CCCM"},
        {"Pipeline": "hvcp-uattt-pc-release-deploy", "X-Center": "PC"},
        {"Pipeline": "hvcp-uattt-cc-release-deploy", "X-Center": "CC"},
        {"Pipeline": "hvcp-uattt-cmcc-release-deploy", "X-Center": "CCCM"},
        {"Pipeline": "hvcp-uattt-mu-master-deploy", "X-Center": "Mule"},
    ],
     "NFT": [
        {"Pipeline": "hvcp-nft-pc-build", "X-Center": "PC"},
        {"Pipeline": "hvcp-nft-cc-build", "X-Center": "CC"},
        {"Pipeline": "hvcp-nft-cccm-build", "X-Center": "CCCM"},
        {"Pipeline": "hvcp-nft-pc-master-deploy", "X-Center": "PC"},
        {"Pipeline": "hvcp-nft-cc-master-deploy", "X-Center": "CC"},
        {"Pipeline": "hvcp-nft-cccm-master-deploy", "X-Center": "CCCM"},
        {"Pipeline": "hvcp-nft-mu-master-deploy", "X-Center": "Mule"},
    ]
}

lower_envs = {    "SIT": [
        {"Pipeline": "hvcp-sit-pc-master-deploy", "X-Center": "PC"},
        {"Pipeline": "hvcp-sit-cc-master-deploy", "X-Center": "CC"},
        {"Pipeline": "hvcp-sit-cccm-master-deploy", "X-Center": "CCCM"},
        {"Pipeline": "hvcp-sit-mu-master-deploy", "X-Center": "Mule"},
    ],
    "E2ETT": [
        {"Pipeline": "hvcp-e2ett-pc-master-deploy", "X-Center": "PC"},
        {"Pipeline": "hvcp-e2ett-cc-master-deploy", "X-Center": "CC"},
        {"Pipeline": "hvcp-e2ett-cccm-master-deploy", "X-Center": "CCCM"},
        {"Pipeline": "hvcp-e2ett-mu-master-deploy", "X-Center": "Mule"},
    ]}

if all_env:
    environments.update(lower_envs)
if lower_env_only:
    environments = lower_envs
# Define a function to check the status of a pipeline and get the latest execution time
def get_pipeline_status(pipeline_name ,client):
    try:
        response = client.get_pipeline_state(name=pipeline_name)
    except ClientError as e:
        if e.response['Error']['Code'] == 'PipelineNotFoundException':
            return {"Stage": 'N/A', "Status": 'N/A', "LastUpdateTime": 'N/A'}
    first_stage_start_time = [x for x in response['stageStates']][0]['actionStates'][0]['latestExecution']['lastStatusChange']
    response = [x for x in response['stageStates'] if x['actionStates'][0]['latestExecution']['lastStatusChange'] > first_stage_start_time ]

    latest_execution = response[-1]
    stage_name = latest_execution['stageName']
    action_states = latest_execution['actionStates']
    status = latest_execution['latestExecution']['status']
    last_update_time = action_states[-1]['latestExecution']['lastStatusChange']
    # latest_execution['lastUpdateTime']
    return {"Stage": stage_name, "Status": status, "LastUpdateTime": last_update_time}

# Initialize a dictionary to store the pipeline statuses
pipeline_statuses = {}


table_data = []

# Iterate through environments and pipeline names
for env, pipelines in environments.items():
    if env == 'NFT':
        client = create_client(region_name, 'codepipeline', 'cthvcpprod')
    else:
        client = create_client(region_name, 'codepipeline', 'hvcpnonprod')
    for pipeline_info in pipelines:
        pipeline_name = pipeline_info["Pipeline"]
        # if not pipeline_name == 'hvcp-uat-pc-release-deploy':
        #     continue
        x_center = pipeline_info["X-Center"]
        status_info = get_pipeline_status(pipeline_name, client)
        # if not pipeline_name == 'hvcp-nft-cc-master-deploy':
        #     continue
        last_update_time = status_info["LastUpdateTime"]
        if last_update_time == 'N/A':
            continue
        # Calculate the time elapsed since the last update
        time_elapsed = datetime.now(pytz.utc) - last_update_time
        # Calculate days, hours, and minutes from the elapsed time
        days, seconds = time_elapsed.days, time_elapsed.seconds
        hours = seconds // 3600 + time_elapsed.days*24
        minutes = (seconds % 3600) // 60 + hours*60
        # Format the Last Update Time without microseconds
        last_update_time_str = last_update_time.strftime('%Y-%m-%d %H:%M:%S')
        # Add Environment and X-Center as the first two columns
        table_data.append([env, x_center, pipeline_name, status_info["Stage"], status_info["Status"], last_update_time_str, f"{minutes} minutes"])


# Filter pipelines with the latest run in the last x hours
x_hours_ago = datetime.now(pytz.utc) - timedelta(hours=3)


recent_table_data = []
for row in table_data:
    if x_hours_ago <= datetime.strptime(row[5], '%Y-%m-%d %H:%M:%S').replace(tzinfo=pytz.utc):
        recent_table_data.append(row)
    else:
        recent_table_data.append([row[0], row[1], row[2],'N/A','Not yet run','N/A','N/A'])

sorted_table_data = sorted(recent_table_data, key=lambda row: (row[0], row[3], row[1]))

# Define the table headers
headers = ["Environment", "X-Center", "Pipeline Name", "Stage", "Status", "Last Update Time", "Time Since Last update"]

# sorted_table_data = [(i + 1, *row) for i, row in enumerate(recent_table_data) if not 'build' in row[2]]
build_info = [row for row in recent_table_data if 'build' in row[2]]
release_info = [row for row in recent_table_data if 'deploy' in row[2]]

build_info = [(i + 1, *row) for i, row in enumerate(build_info) ]
release_info = [(i + 1, *row) for i, row in enumerate(release_info) ]


print("Build Pipeline statuses for the last 3 hours:")
# print(tabulate(sorted_table_data, headers=headers, tablefmt="pretty", showindex=True))
print(tabulate(build_info, headers=["S/No."] + headers, tablefmt="pretty", showindex=False, stralign='left'))


print("\n\nRelease Pipeline statuses for the last 3 hours:")
# print(tabulate(sorted_table_data, headers=headers, tablefmt="pretty", showindex=True))
print(tabulate(release_info, headers=["S/No."] + headers, tablefmt="pretty", showindex=False, stralign='left'))

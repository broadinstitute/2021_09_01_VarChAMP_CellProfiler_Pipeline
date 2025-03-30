## 1. File transfer

Pending to be updated...

## 2. Create CSVs
============================================================================================
### 2.1 Check the .xml file for imaged channels
============================================================================================
- Note: Batch 11 has two microscopes, confocal and widefield, and I want to check if the two microsopes have different Index.idx.xml's

* Confocal:
aws s3 cp s3://cellpainting-gallery/cpg0020-varchamp/broad/images/2024_12_09_Batch_11/images/2024-12-09_B11A1R1__2024-12-09T08_49_55-Measurement_1/Images/Index.idx.xml 2_create_csv/Index.idx.xml

* Widefield:
aws s3 cp s3://cellpainting-gallery/cpg0020-varchamp/broad/images/2024_12_09_Batch_11/images/2024-12-09_B11A1R1_widefield__2024-12-09T13_40_28-Measurement_1/Images/Index.idx.xml 2_create_csv/Index_widefield.idx.xml

- Read the channel names from the last 500 lines of the .xml file
tail -n 500 2_create_csv/Index.idx.xml | grep ChannelName | sort -u
      <ChannelName>Alexa 488</ChannelName>
      <ChannelName>Alexa 568</ChannelName>
      <ChannelName>Brightfield</ChannelName>
      <ChannelName>Brightfield High</ChannelName>
      <ChannelName>Brightfield Low</ChannelName>
      <ChannelName>DAPI</ChannelName>
      <ChannelName>MitoTracker Deep Red</ChannelName>

tail -n 500 2_create_csv/Index_widefield.idx.xml | grep ChannelName | sort -u
      <ChannelName>Alexa 488</ChannelName>
      <ChannelName>Alexa 568</ChannelName>
      <ChannelName>DAPI</ChannelName>
      <ChannelName>MitoTracker Deep Red</ChannelName>

They are indeed different from each other, thus require different metadata files for downstream processing.

============================================================================================
### 2.2 Create metadata file(s)
============================================================================================
If you would like to make CSVs for all the plates in your batch (typical), leave exclude_plates and include_plates as empty lists ([]). If there are plates in your batch folder that you specifically want to exclude from CSV creation, list them in exclude_plates using the shortened plate name (before the __) (e.g. "exclude_plates":["BR00126551","BR00126552","BR00126553"]). If you only want to create CSVs for a specific plate or subset of plates, list them in include_plates in a similar manner.

For VarChAMP data, we use the following meta data to map each image channel to the cell compartment it corresponds to:

* Confocal metadata file:
============================================================================================
{ "exclude_plates":[],
"include_plates":["2024-12-09_B11A1R1"],
"project_name":"cpg0020-varchamp",
"batch":"2024_12_09_Batch_11",
"zproject":false,
"bucket": "cellpainting-gallery",
"bucket_out": "imaging-platform",
"channeldict":{
"Alexa 488":"OrigGFP", 
"Alexa 568":"OrigAGP", 
"Brightfield High":"OrigBrightfield_H", 
"Brightfield Low":"OrigBrightfield_L", 
"Brightfield":"OrigBrightfield", 
"DAPI":"OrigDNA", 
"MitoTracker Deep Red":"OrigMito"
},
"run_pe2loaddata": true,
"platename_replacementdict":{
    "2024-12-09_B11A1R1__2024-12-09T08_49_55-Measurement_1":"2024-12-09_B11A1R1"
},
"source":"broad"
}
============================================================================================

* Widefield metadata file:
============================================================================================
{ "exclude_plates":[],
"include_plates":["2024-12-09_B11A1R1_widefield"],
"project_name":"cpg0020-varchamp",
"batch":"2024_12_09_Batch_11",
"zproject":false,
"bucket": "cellpainting-gallery",
"bucket_out": "imaging-platform",
"channeldict":{
"Alexa 488": "OrigGFP", 
"Alexa 568": "OrigAGP", 
"DAPI": "OrigDNA", 
"MitoTracker Deep Red": "OrigMito"
},
"run_pe2loaddata": true,
"platename_replacementdict":{
    "2024-12-09_B11A1R1_widefield__2024-12-09T13_40_28-Measurement_1":"2024-12-09_B11A1R1_widefield"
},
"source":"broad"
}
============================================================================================

============================================================================================
### 2.3 Run the Step Function
============================================================================================
In the AWS Console, go to Step Functions. If your images are in the cellpainting-gallery, select pe2loaddata_cpg => Start execution 
(If your images are in a bucket we own, select pe2loaddata => Start execution, irrelavant to VarChAMP).
      Name = (No need to change the hash it generates)       Input = copy and paste in the metadata you created.

============================================================================================
### 2.4 Troubleshooting the Step Function if needed
============================================================================================

============================================================================================
### 2.5 Check your CSV creation
============================================================================================
Download files to local computer for examine:
aws s3 sync s3://imaging-platform/cpg0020-varchamp/broad/workspace/load_data_csv/2024_12_09_Batch_11/ 2_create_csv/load_data_csv/2024_12_09_Batch_11/
aws s3 sync s3://imaging-platform/cpg0020-varchamp/broad/workspace/load_data_csv_orig/2024_12_09_Batch_11/ 2_create_csv/load_data_csv_orig/2024_12_09_Batch_11/

#### Issues detected!!!
In confocal plates, something's wrong with the step function and the file path was messed up.
##### Fixing issues:
To fix the issues, replace:
- whole document:   `2024-12-09 1% rescreen R1` --> `2024-12-09_B11A1R1`
                    `2024-12-09_B11A1R1_widefield__2024-12-09T13_40_28-Measurement_1` --> `2024-12-09_B11A1R1__2024-12-09T08_49_55-Measurement_1`
Using fix_issues.ipynb

============================================================================================
### 2.6 Transfer load_data.csv to CPG
============================================================================================
#### Reformat first (no longer needed when using pe2loaddata_cpg)
python ../standardize2cpg.py --input_path 2_create_csv/load_data_csv_orig/ --out_path 2_create_csv/load_data_csv/

#### Re-upload data files to expected dir within our bucket
OUR_BUCKET=imaging-platform
CPG_IDENTIFIER=cpg0020-varchamp
BATCH_ID=2024_12_09_Batch_11
SOURCE=broad

aws s3 cp --recursive 2_create_csv/load_data_csv/${BATCH_ID}/ s3://${OUR_BUCKET}/${CPG_IDENTIFIER}/${SOURCE}/workspace/load_data_csv/${BATCH_ID}/
aws s3 cp --recursive 2_create_csv/load_data_csv_orig/${BATCH_ID}/ s3://${OUR_BUCKET}/${CPG_IDENTIFIER}/${SOURCE}/workspace/load_data_csv_orig/${BATCH_ID}/

bash ../upload_s3_data.sh
aws s3 cp --recursive --profile jump-cp-role 2_create_csv/load_data_csv/${BATCH_ID}/ s3://cellpainting-gallery/${CPG_IDENTIFIER}/${SOURCE}/workspace/load_data_csv/${BATCH_ID}/
aws s3 cp --recursive --profile jump-cp-role 2_create_csv/load_data_csv_orig/${BATCH_ID}/ s3://cellpainting-gallery/${CPG_IDENTIFIER}/${SOURCE}/workspace/load_data_csv_orig/${BATCH_ID}/

## 3. Illumination correction

### 3.1 Start and login to DCP machine
ssh -i ".ssh/shenrunx.pem" ubuntu@Public_IPv4_DNS ##ec2-13-218-165-13.compute-1.amazonaws.com

### 3.2 Define env vars
PROJECT_NAME=cpg0020-varchamp
BATCH_ID=2024_12_09_Batch_11
BUCKET=imaging-platform

### 3.3 Activate pyenv
pyenv shell 3.8.10 #broad-imaging

### 3.4 Create dirs
mkdir -p ~/efs/${PROJECT_NAME}/workspace/
cd ~/efs/${PROJECT_NAME}/workspace/
mkdir -p log/${BATCH_ID}

### 3.5 Download DCP for the first time
cd ~/efs/${PROJECT_NAME}/workspace/
mkdir software
cd software
git clone https://github.com/CellProfiler/Distributed-CellProfiler.git
cd ..

#### Add my aws config to the .aws/config on DCP. !!!
[profile jump-cp-role]
role_arn = arn:aws:iam::385009899373:role/add-jump-cp-role
source_profile = default

cd ~/efs/cpg0020-varchamp/workspace/software/Distributed-CellProfiler

#### Modify the config.py as below:
##### This is my own AWS config
============================================================================================
##### Constants (User configurable)
APP_NAME = 'cpg0020-varchamp_Illum'                # Used to generate derivative names unique to the application.
LOG_GROUP_NAME = APP_NAME

##### DOCKER REGISTRY INFORMATION:
DOCKERHUB_TAG = 'cellprofiler/distributed-cellprofiler:2.2.0_4.2.8'

##### AWS GENERAL SETTINGS:
AWS_REGION = 'us-east-1'
AWS_PROFILE = 'jump-cp-role'                 # The same profile used by your AWS CLI installation
SSH_KEY_NAME = 'shenrunx.pem'      # Expected to be in ~/.ssh
AWS_BUCKET = 'imaging-platform'         # Bucket to use for logging
SOURCE_BUCKET = 'cellpainting-gallery'           # Bucket to download image files from
WORKSPACE_BUCKET = 'imaging-platform'        # Bucket to download non-image files from
DESTINATION_BUCKET = 'cellpainting-gallery'      # Bucket to upload files to

##### EC2 AND ECS INFORMATION:
ECS_CLUSTER = 'default'
CLUSTER_MACHINES = 1
TASKS_PER_MACHINE = 1
MACHINE_TYPE = ['m5.xlarge']
MACHINE_PRICE = 0.20
EBS_VOL_SIZE = 200                       # In GB.  Minimum allowed is 22.
DOWNLOAD_FILES = 'True'
ASSIGN_IP = 'True'                     # If false, will overwrite setting in Fleet file

##### DOCKER INSTANCE RUNNING ENVIRONMENT:
DOCKER_CORES = 4                        # Number of CellProfiler processes to run inside a docker container
CPU_SHARES = DOCKER_CORES * 1024        # ECS computing units assigned to each docker container (1024 units = 1 core)
MEMORY = 15000                           # Memory assigned to the docker container in MB
SECONDS_TO_START = 3*60                 # Wait before the next CP process is initiated to avoid memory collisions

##### SQS QUEUE INFORMATION:
SQS_QUEUE_NAME = APP_NAME + 'Queue'
SQS_MESSAGE_VISIBILITY = 240*60           # Timeout (secs) for messages in flight (average time to be processed)
SQS_DEAD_LETTER_QUEUE = 'user_DeadMessages'
JOB_RETRIES = 3            # Number of times to retry a job before sending it to DEAD_LETTER_QUEUE

##### MONITORING
AUTO_MONITOR = 'True'

##### CLOUDWATCH DASHBOARD CREATION
CREATE_DASHBOARD = 'True'           # Create a dashboard in Cloudwatch for run
CLEAN_DASHBOARD = 'True'            # Automatically remove dashboard at end of run with Monitor

##### REDUNDANCY CHECKS
CHECK_IF_DONE_BOOL = 'False'  #True or False- should it check if there are a certain number of non-empty files and delete the job if yes?
EXPECTED_NUMBER_FILES = 7    #What is the number of files that trigger skipping a job?
MIN_FILE_SIZE_BYTES = 1      #What is the minimal number of bytes an object should be to "count"?
NECESSARY_STRING = ''        #Is there any string that should be in the file name to "count"?

##### CELLPROFILER SETTINGS
ALWAYS_CONTINUE = 'False'     # Whether or not to run CellProfiler with the --always-continue flag, which will keep CellProfiler from crashing if it errors

##### PLUGINS
USE_PLUGINS = 'False'          # True to use any plugin from CellProfiler-plugins repo
UPDATE_PLUGINS = 'False'       # True to download updates from CellProfiler-plugins repo
PLUGINS_COMMIT = 'False'       # What commit or version tag do you want to check out? If not, set to False.
INSTALL_REQUIREMENTS = 'False' # True to install REQUIREMENTS defined below. Requirements should have all plugin dependencies.
REQUIREMENTS = ''       # Flag to use with install (current) or path within the CellProfiler-plugins repo to a requirements file (deprecated).
============================================================================================

### 3.6 Execute
python3 run.py setup

#### Successful output: 
============================================================================================
DeadLetter queue user_DeadMessages already exists.
Queue exists
Cluster default exists
Using role for credentials arn:aws:iam::385009899373:role/add-jump-cp-role
Task definition registered
Creating new service
Service created
============================================================================================

### 3.7 Create jobs

#### Download the previous recipes first:
aws s3 sync s3://cellpainting-gallery/cpg0020-varchamp/broad/workspace/pipelines/2024_12_09_Batch_12 2024_12_09_Batch_12

PROJECT_NAME=cpg0020-varchamp
BUCKET=imaging-platform
BATCH_ID=2024_12_09_Batch_11
SOURCE=broad

#### Submit Jobs
python run_batch_general.py illum ${PROJECT_NAME} ${BATCH_ID} "2024-12-09_B11A1R1" \
--path-style cpg \
--source ${SOURCE} \
--pipeline illum_confocal.cppipe \
--pipeline-path ${PROJECT_NAME}/${SOURCE}/workspace/pipelines/2024_12_09_Batch_12/ \
--datafile-path ${PROJECT_NAME}/${SOURCE}/workspace/load_data_csv_orig/2024_12_09_Batch_11/

python run_batch_general.py illum ${PROJECT_NAME} ${BATCH_ID} "2024-12-09_B11A1R1_widefield" \
--path-style cpg \
--source ${SOURCE} \
--pipeline illum_widefield.cppipe \
--pipeline-path ${PROJECT_NAME}/${SOURCE}/workspace/pipelines/2024_12_09_Batch_12/ \
--datafile-path ${PROJECT_NAME}/${SOURCE}/workspace/load_data_csv_orig/2024_12_09_Batch_11/

#### Start spot fleet
============================================================================================
{
"IamFleetRole": "arn:aws:iam::385009899373:role/aws-ec2-spot-fleet-role",
"AllocationStrategy": "lowestPrice",
"TerminateInstancesWithExpiration": true,
"LaunchSpecifications": [
{
"ImageId": "ami-0ce03502c5bb5e188",
"KeyName": "shenrunx", ## change it to your own user name
"IamInstanceProfile": {
"Arn": "arn:aws:iam::385009899373:instance-profile/ecsInstanceRole"
},
"BlockDeviceMappings": [
{
    "DeviceName": "/dev/xvda",
    "Ebs": {
    "DeleteOnTermination": true,
    "VolumeType": "gp3",
    "VolumeSize": 8,
    "SnapshotId": "snap-0a7b4ece894d62882"
}
},
{
"DeviceName": "/dev/xvdcz",
"Ebs": {
    "DeleteOnTermination": true,
    "VolumeType": "gp3"
}
}
],
"NetworkInterfaces": [
{
"DeviceIndex": 0,
"SubnetId": "subnet-55625c0d",
"DeleteOnTermination": true,
"AssociatePublicIpAddress": true,
"Groups": [
    "sg-74b99a0f"
]
}
]
}
],
"Type": "maintain"
}
============================================================================================
python3 run.py startCluster files/Fleet.json

#### Monitor the progress
python run.py monitor files/${PROJECT_NAME}_IllumSpotFleetRequestId.json

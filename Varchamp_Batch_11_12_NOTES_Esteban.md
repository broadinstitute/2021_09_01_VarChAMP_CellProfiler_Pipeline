# Varchamp Batch_10

## Upload images to the staging bucket for the CPG

- I have credentials for the CPG that Ank created (`cpg-staging` profile), but those have to be created for each prefix (aka dataset-id)

- Follow the instructions in the [Cellpainting Gallery docuemntation for uploading to the Gallery](https://broadinstitute.github.io/cellpainting-gallery/uploading_to_cpg.html)
    - Already asked Ank for credentials
    - Installed jq (in my local computer, how does this work for uploading from the dropbox?)
    - I haven't received new credentials so I will use the ones I have already
    - Created `Documents/GitHub/emiglietta_projects/2024_Varchamp/Batch_EM2/create_credentials.sh`
    - Run `source Documents/GitHub/emiglietta_projects/2024_Varchamp/Batch_EM2/create_credentials.sh`
        `AWS credentials have been set successfully.`

# Upload files from dropbox to AWS

- Must logged in Broad-internal or VPN
- In command line, login to: 
    `ssh emigliet@login01.broadinstitute.org`  
- Introduce personal password

## Generate an interactive session on the cluster with 4GB of RAM and 4 CPUs.
```
tmux new -s upload -OR- tmux attach -t upload
reuse UGER
ish -l h_vmem=4G -pe smp 4

BUCKET=staging-cellpainting-gallery
PROJECT_NAME=cpg0020-varchamp
BATCH_ID=2024_12_09_Batch_11

```

## Check the files the collaborator shared
```
cd /imaging/dropbox/VarChAMP/
ls /imaging/dropbox/VarChAMP/
    2024-12-09 B11A1R1__2024-12-09T08_49_55-Measurement 1/
    2024-12-09 B11A1R1_widefield__2024-12-09T13_40_28-Measurement 1/
    2024-12-09 B12A1R2__2024-12-09T10_34_39-Measurement 1/
    2024-12-09 B12A1R2_widefield__2024-12-09T12_27_55-Measurement 1/
```
- IMPORTANT! --> change the name of the folders so that they don't have any spaces!

- The images are in the imaging dropbox, which is accesed from the Broad server, which operates on Linux, so:
    - cannot install jq in the server --> ` sudo apt-get install jq` --> don't have SUDO permissions for the server (makes sense!)
        - I need to include jq in the software available in your UGER session:
            - Log in to the server: ssh YOUR_BROAD_USERNAME@login.broadinstitute.org
            - nano ~/.my.bashrc
            - Under `Dotkits` add at the end: use jq
            - Save (ctrl+O) and exit (ctrl+x)
    - Still, I cannot run `source /imaging/dropbox/VarChAMP/create_credentials.sh` because of some weird issue with the version of AWS or sth.
    - As a workaround, I ran `source Documents/GitHub/emiglietta_projects/2024_Varchamp/Batch_EM2/create_credentials.sh` on my local computer and copy the generated environmental variables over to the session in the server:
        echo $AWS_ACCESS_KEY_ID
        echo $AWS_SECRET_ACCESS_KEY
        echo $AWS_SESSION_TOKEN

## Run transfer command

- I had to run `aws configure` to input my aws credentials within the Broad Server (I deleted them afterwards just in case).
- I nano'ed into the credentials (`nano ~/.aws/credentials`) and added my cpg_staging credentials manually:
	export AWS_ACCESS_KEY_ID=
	export AWS_SECRET_ACCESS_KEY=
	export AWS_SESSION_TOKEN=
- For some reason, `aws s3 sync` errors, but running `aws s3 cp --recursive` seems to work just fine:


aws s3 cp --recursive /imaging/dropbox/VarChAMP/2024_12_09_Batch_11/ s3://staging-cellpainting-gallery/cpg0020-varchamp/broad/images/2024_12_09_Batch_11/ --acl bucket-owner-full-control

aws s3 cp --recursive /imaging/dropbox/VarChAMP/2024_12_09_Batch_12/ s3://staging-cellpainting-gallery/cpg0020-varchamp/broad/images/2024_12_09_Batch_12/ --acl bucket-owner-full-control





aws s3 mv s3://staging-cellpainting-gallery/cpg0020-varchamp/broad/images/2024_12_09_Batch_10/ s3://staging-cellpainting-gallery/cpg0020-varchamp/broad/images/2024_12_09_Batch_11/ --recursive --exclude "*" --include "2024-12-09 B11A1R1*"

aws s3 mv s3://staging-cellpainting-gallery/cpg0020-varchamp/broad/images/2024_12_09_Batch_10/ s3://staging-cellpainting-gallery/cpg0020-varchamp/broad/images/2024_12_09_Batch_11/ --recursive --exclude "*" --include "2024-12-09 B12A1R2*"

=======================
Create load_data.csv
=======================

- Check index.xml file:

aws s3 cp s3://cell-painting-gallery/cpg0020-varchamp/broad/images/2024_12_09_Batch_11/images/2024-12-09_B11A1R1__2024-12-09T08_49_55-Measurement_1/Images/Index.idx.xml /Users/emigliet/Documents/GitHub/emiglietta_projects/2024_Varchamp/

tail -n 500 /Users/emigliet/Documents/GitHub/emiglietta_projects/2024_Varchamp/Batch_EM2/Index_confocal.idx.xml|grep ChannelName|sort -u
      <ChannelName>Alexa 488</ChannelName>
      <ChannelName>Alexa 568</ChannelName>
      <ChannelName>Brightfield High</ChannelName>
      <ChannelName>Brightfield Low</ChannelName>
      <ChannelName>Brightfield</ChannelName>
      <ChannelName>DAPI</ChannelName>
      <ChannelName>MitoTracker Deep Red</ChannelName>

tail -n 500 /Users/emigliet/Documents/GitHub/emiglietta_projects/2024_Varchamp/Batch_EM2/Index_widefield.idx.xml|grep ChannelName|sort -u
      <ChannelName>Alexa 488</ChannelName>
      <ChannelName>Alexa 568</ChannelName>
      <ChannelName>DAPI</ChannelName>
      <ChannelName>MitoTracker Deep Red</ChannelName>


2024-12-09 B11A1R1__2024-12-09T08_49_55-Measurement 1/
2024-12-09 B11A1R1_widefield__2024-12-09T13_40_28-Measurement 1/
2024-12-09 B12A1R2__2024-12-09T10_34_39-Measurement 1/
2024-12-09 B12A1R2_widefield__2024-12-09T12_27_55-Measurement 1/

============================================================================================
## Create load_data.csv file
**In the AWS Console, go to Step Functions. Select pe2loaddata => Start execution**
============================================================================================
If you would like to make CSVs for all the plates in your batch (typical), leave exclude_plates and include_plates as 
empty lists ([]). If there are plates in your batch folder that you specifically want to exclude from CSV creation, list
them in exclude_plates using the shortened plate name (before the __) (e.g. "exclude_plates":["BR00126551","BR00126552",
"BR00126553"]). If you only want to create CSVs for a specific plate or subset of plates, list them in include_plates in 
a similar manner.
============================================================================================
{ "exclude_plates":[],
"include_plates":["2024-12-09_B11A1R1"],
"project_name":"cpg0020-varchamp",
"batch":"2024_12_09_Batch_11",
"zproject":false,
"bucket": "cellpainting-gallery",
"bucket_out": "imaging-platform-ssf",
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
{ "exclude_plates":[],
"include_plates":["2024-12-09_B11A1R1_widefield"],
"project_name":"cpg0020-varchamp",
"batch":"2024_12_09_Batch_11",
"zproject":false,
"bucket": "cellpainting-gallery",
"bucket_out": "imaging-platform-ssf",
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
{ "exclude_plates":["2024-12-09_B12A1R2_widefield"],
"include_plates":[],
"project_name":"cpg0020-varchamp",
"batch":"2024_12_09_Batch_12",
"zproject":false,
"bucket": "cellpainting-gallery",
"bucket_out": "imaging-platform-ssf",
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
    "2024-12-09_B12A1R2__2024-12-09T10_34_39-Measurement_1":"2024-12-09_B12A1R2"
},
"source":"broad"
}

============================================================================================
{ "exclude_plates":[],
"include_plates":["2024-12-09_B12A1R2_widefield"],
"project_name":"cpg0020-varchamp",
"batch":"2024_12_09_Batch_12",
"zproject":false,
"bucket": "cellpainting-gallery",
"bucket_out": "imaging-platform-ssf",
"channeldict":{
"Alexa 488": "OrigGFP", 
"Alexa 568": "OrigAGP", 
"DAPI": "OrigDNA", 
"MitoTracker Deep Red": "OrigMito"
},
"run_pe2loaddata": true,
"platename_replacementdict":{
    "2024-12-09_B12A1R2_widefield__2024-12-09T12_27_55-Measurement_1":"2024-12-09_B12A1R2_widefield"
},
"source":"broad"
}
============================================================================================

## Transfer load_data.csv’s to CPG --> NOT NECESSARY!

### Download files to local computer
aws s3 sync s3://imaging-platform-ssf/cpg0020-varchamp/broad/workspace/load_data_csv/2024_12_09_Batch_11/ /Users/emigliet/Documents/GitHub/emiglietta_projects/2024_Varchamp/Batch_EM2/2024_12_09_Batch_11/

aws s3 sync s3://imaging-platform-ssf/cpg0020-varchamp/broad/workspace/load_data_csv/2024_12_09_Batch_12/ /Users/emigliet/Documents/GitHub/emiglietta_projects/2024_Varchamp/Batch_EM2/2024_12_09_Batch_12/



- Run `source Documents/GitHub/emiglietta_projects/2024_Varchamp/Batch_EM2/create_credentials.sh`
        `AWS credentials have been set successfully.`

- Run `env | grep AWS` to check that the environmental variables were sucessfully created 

aws s3 cp --recursive /Users/emigliet/Documents/GitHub/emiglietta_projects/2024_Varchamp/Batch_EM2/2024_12_09_Batch_11/ s3://staging-cellpainting-gallery/cpg0020-varchamp/broad/workspace/load_data_csv/2024_12_09_Batch_11/ --acl bucket-owner-full-control

aws s3 cp --recursive /Users/emigliet/Documents/GitHub/emiglietta_projects/2024_Varchamp/Batch_EM2/2024_12_09_Batch_12/ s3://staging-cellpainting-gallery/cpg0020-varchamp/broad/workspace/load_data_csv/2024_12_09_Batch_12/ --acl bucket-owner-full-control

### Confirm upload to staging bucket:
aws s3 ls --recursive --human-readable s3://staging-cellpainting-gallery/cpg0020-varchamp/broad/workspace/load_data_csv/2024_12_09_Batch_11/
    2025-01-21 17:50:48    4.7 MiB cpg0020-varchamp/broad/workspace/load_data_csv/2024_12_09_Batch_11/2024-12-09_B11A1R1/load_data.csv
    2025-01-21 17:50:49    7.7 MiB cpg0020-varchamp/broad/workspace/load_data_csv/2024_12_09_Batch_11/2024-12-09_B11A1R1/load_data_with_illum.csv
    2025-01-21 17:50:49    3.0 MiB cpg0020-varchamp/broad/workspace/load_data_csv/2024_12_09_Batch_11/2024-12-09_B11A1R1_widefield/load_data.csv
    2025-01-21 17:50:49    5.0 MiB cpg0020-varchamp/broad/workspace/load_data_csv/2024_12_09_Batch_11/2024-12-09_B11A1R1_widefield/load_data_with_illum.csv

aws s3 ls --recursive --human-readable s3://staging-cellpainting-gallery/cpg0020-varchamp/broad/workspace/load_data_csv/2024_12_09_Batch_12/
    2025-01-21 17:51:07    4.7 MiB cpg0020-varchamp/broad/workspace/load_data_csv/2024_12_09_Batch_12/2024-12-09_B12A1R2/load_data.csv
    2025-01-21 17:51:07    7.8 MiB cpg0020-varchamp/broad/workspace/load_data_csv/2024_12_09_Batch_12/2024-12-09_B12A1R2/load_data_with_illum.csv
    2025-01-21 17:51:07    3.0 MiB cpg0020-varchamp/broad/workspace/load_data_csv/2024_12_09_Batch_12/2024-12-09_B12A1R2_widefield/load_data.csv
    2025-01-21 17:51:07    5.0 MiB cpg0020-varchamp/broad/workspace/load_data_csv/2024_12_09_Batch_12/2024-12-09_B12A1R2_widefield/load_data_with_illum.csv

- Erin told me that the load_data.csv should stay in our bucket for now, so I delete what I uploaded to the staging bucket:
    aws s3 rm --recursive s3://staging-cellpainting-gallery/cpg0020-varchamp/broad/workspace/load_data_csv/2024_12_09_Batch_11/
    aws s3 rm --recursive s3://staging-cellpainting-gallery/cpg0020-varchamp/broad/workspace/load_data_csv/2024_12_09_Batch_12/


## Move load data files to expected dir within our bucket

aws s3 mv --recursive s3://imaging-platform-ssf/cpg0020-varchamp/broad/workspace/load_data_csv/2024_12_09_Batch_11/ s3://imaging-platform-ssf/projects/cpg0020-varchamp/workspace/load_data_csv/2024_12_09_Batch_11/
aws s3 mv --recursive s3://imaging-platform-ssf/cpg0020-varchamp/broad/workspace/load_data_csv/2024_12_09_Batch_12/ s3://imaging-platform-ssf/projects/cpg0020-varchamp/workspace/load_data_csv/2024_12_09_Batch_12/

aws s3 sync s3://imaging-platform-ssf/projects/cpg0020-varchamp/workspace/load_data_csv/ s3://imaging-platform-ssf/cpg0020-varchamp/broad/workspace/load_data_csv/ --dryrun

=========================================

# Set up for Illum

## Download the pipelines used for Bath_9 to DCP machine
pyenv shell 3.8.13 #broad-imaging-cimini
mkdir ~/efs/cpg0020-varchamp/workspace/pipelines/
mkdir ~/efs/cpg0020-varchamp/workspace/pipelines/Batch_9/
cd ~/efs/cpg0020-varchamp/workspace/pipelines
aws s3 sync s3://imaging-platform-ssf/projects/2021_09_21_VarChAMP/workspace/pipelines/Batch_EM1/ .


# Set variables

PROJECT_NAME=cpg0020-varchamp
BATCH_ID=2024_12_09_Batch_11
BUCKET=cellpainting-gallery
pyenv shell 3.8.13 #broad-imaging-cimini
-----------------------------------------------------------------------------------------------------------------------------------------------------------------
# Constants (User configurable)

APP_NAME = 'cpg0020-varchamp_Illum'                # Used to generate derivative names unique to the application.
LOG_GROUP_NAME = APP_NAME

# DOCKER REGISTRY INFORMATION:
DOCKERHUB_TAG = 'cellprofiler/distributed-cellprofiler:2.2.0_4.2.8'

# AWS GENERAL SETTINGS:
AWS_REGION = 'us-east-1'
AWS_PROFILE = 'cpg-access-role'                 # The same profile used by your AWS CLI installation
SSH_KEY_NAME = 'EstebanMiglietta_BroadInstitute_US-esat-1.pem'      # Expected to be in ~/.ssh
AWS_BUCKET = 'imaging-platform-ssf'         # Bucket to use for logging
SOURCE_BUCKET = 'cellpainting-gallery'           # Bucket to download image files from
WORKSPACE_BUCKET = 'imaging-platform-ssf'        # Bucket to download non-image files from
DESTINATION_BUCKET = 'cellpainting-gallery'      # Bucket to upload files to
UPLOAD_FLAGS = '--acl bucket-owner-full-control'    # Any flags needed for upload to destination bucket

# EC2 AND ECS INFORMATION:
ECS_CLUSTER = 'default'
CLUSTER_MACHINES = 1
TASKS_PER_MACHINE = 1
MACHINE_TYPE = ['c5.xlarge']            # c5.xlarge has 4 CPUs and 8GB of memory
MACHINE_PRICE = 0.20
EBS_VOL_SIZE = 200                       # In GB.  Minimum allowed is 22.
DOWNLOAD_FILES = 'True'
ASSIGN_IP = 'True'                     # If false, will overwrite setting in Fleet file

# DOCKER INSTANCE RUNNING ENVIRONMENT:
DOCKER_CORES = 4                        # Number of CellProfiler processes to run inside a docker container
CPU_SHARES = DOCKER_CORES * 1024        # ECS computing units assigned to each docker container (1024 units = 1 core)
MEMORY = 7500                           # Memory assigned to the docker container in MB
SECONDS_TO_START = 3*60                 # Wait before the next CP process is initiated to avoid memory collisions

# SQS QUEUE INFORMATION:
SQS_QUEUE_NAME = APP_NAME + 'Queue'
SQS_MESSAGE_VISIBILITY = 240*60           # Timeout (secs) for messages in flight (average time to be processed)
SQS_DEAD_LETTER_QUEUE = 'user_DeadMessages'
JOB_RETRIES = 3            # Number of times to retry a job before sending it to DEAD_LETTER_QUEUE

# MONITORING
AUTO_MONITOR = 'True'

# CLOUDWATCH DASHBOARD CREATION
CREATE_DASHBOARD = 'True'           # Create a dashboard in Cloudwatch for run
CLEAN_DASHBOARD = 'True'            # Automatically remove dashboard at end of run with Monitor

# REDUNDANCY CHECKS
CHECK_IF_DONE_BOOL = 'False'  #True or False- should it check if there are a certain number of non-empty files and delete the job if yes?
EXPECTED_NUMBER_FILES = 7    #What is the number of files that trigger skipping a job?
MIN_FILE_SIZE_BYTES = 1      #What is the minimal number of bytes an object should be to "count"?
NECESSARY_STRING = ''        #Is there any string that should be in the file name to "count"?

# CELLPROFILER SETTINGS
ALWAYS_CONTINUE = 'False'     # Whether or not to run CellProfiler with the --always-continue flag, which will keep CellProfiler from crashing if it errors

# PLUGINS
USE_PLUGINS = 'False'          # True to use any plugin from CellProfiler-plugins repo
UPDATE_PLUGINS = 'False'       # True to download updates from CellProfiler-plugins repo
PLUGINS_COMMIT = 'False'       # What commit or version tag do you want to check out? If not, set to False.
INSTALL_REQUIREMENTS = 'False' # True to install REQUIREMENTS defined below. Requirements should have all plugin dependencies.
REQUIREMENTS = ''       # Flag to use with install (current) or path within the CellProfiler-plugins repo to a requirements file (deprecated).

-----------------------------------------------------------------------------------------------------------------------------------------------------------------

## Create queue
python3 run.py setup

## Create jobs

PROJECT_NAME=cpg0020-varchamp
BUCKET=imaging-platform-ssf
BATCH_ID=2024_12_09_Batch_11
BATCH_ID=2024_12_09_Batch_12

python run_batch_general.py illum cpg0020-varchamp 2024_12_09_Batch_11 "2024-12-09_B11A1R1" \
--source broad \
--path-style cpg \
--pipeline illum_confocal.cppipe \
--pipeline-path projects/cpg0020-varchamp/workspace/pipelines/2024_12_09_Batch_11/ \
--datafile-path projects/cpg0020-varchamp/workspace/load_data_csv/2024_12_09_Batch_11/

python run_batch_general.py illum cpg0020-varchamp 2024_12_09_Batch_12 "2024-12-09_B12A1R2" \
--source broad \
--path-style cpg \
--pipeline illum_confocal.cppipe \
--pipeline-path projects/cpg0020-varchamp/workspace/pipelines/2024_12_09_Batch_11/ \
--datafile-path projects/cpg0020-varchamp/workspace/load_data_csv/2024_12_09_Batch_12/

python run_batch_general.py illum cpg0020-varchamp 2024_12_09_Batch_11 "2024-12-09_B11A1R1_widefield" \
--source broad \
--path-style cpg \
--pipeline illum_widefield.cppipe \
--pipeline-path projects/cpg0020-varchamp/workspace/pipelines/2024_12_09_Batch_11/ \
--datafile-path projects/cpg0020-varchamp/workspace/load_data_csv/2024_12_09_Batch_11/

python run_batch_general.py illum cpg0020-varchamp 2024_12_09_Batch_12 "2024-12-09_B12A1R2_widefield" \
--source broad \
--path-style cpg \
--pipeline illum_widefield.cppipe \
--pipeline-path projects/cpg0020-varchamp/workspace/pipelines/2024_12_09_Batch_11/ \
--datafile-path projects/cpg0020-varchamp/workspace/load_data_csv/2024_12_09_Batch_12/

## Start Spot Fleet
python3 run.py startCluster files/Fleet.json
python run.py monitor files/cpg0020-varchamp_IllumSpotFleetRequestId.json

## I need to redo the confocal plates' illum bc they were identical to the widefiled (at least B11A1R1, the other failed)
## The reason is that the load data files pointed to the _widefield images for some reason


## Download the files created by pe2loaddata to check/edit them locally
aws s3 sync s3://imaging-platform-ssf/cpg0020-varchamp/broad/workspace/load_data_csv/ /Users/emigliet/Documents/GitHub/emiglietta_projects/2024_Varchamp/load_data_csv/
# aws s3 sync s3://imaging-platform-ssf/projects/cpg0020-varchamp/workspace/load_data_csv/ /Users/emigliet/Documents/GitHub/emiglietta_projects/2024_Varchamp/load_data_csv/

In confocal plates, replace:
- metadata_plate:   `2024-12-09 1% rescreen R1` --> `2024-12-09_B11A1R1`
                    `2024-12-09 1% rescreen R2` --> `2024-12-09_B12A1R2`
- whole document:   `2024-12-09_B11A1R1_widefield__2024-12-09T13_40_28-Measurement_1` --> `2024-12-09_B11A1R1__2024-12-09T08_49_55-Measurement_1`
                    `2024-12-09_B12A1R2_widefield__2024-12-09T12_27_55-Measurement_1` --> `2024-12-09_B12A1R2__2024-12-09T10_34_39-Measurement_1`

## Reupload to correct location in our bucket
aws s3 sync /Users/emigliet/Documents/GitHub/emiglietta_projects/2024_Varchamp/load_data_csv/ s3://imaging-platform-ssf/projects/cpg0020-varchamp/workspace/load_data_csv/

## Remove the files created by pe2loaddata
aws s3 rm --recursive s3://imaging-platform-ssf/cpg0020-varchamp/

## Illum step was succesful!!
## Widefield Illum files for batch 11 and 12 look VERY VERY similar, but I checked and are not the exact same :)

==============================================
# ASSAY DEV
==============================================
## Calculate size of the volume to attach to AssayDev machine
aws s3 ls s3://cellpainting-gallery/cpg0020-varchamp/broad/images/2024_12_09_Batch_11/ --recursive --summarize --human-readable
    Total Objects: 38032
    Total Size: 74.2 GiB

aws s3 ls s3://cellpainting-gallery/cpg0020-varchamp/broad/images/2024_12_09_Batch_12/ --recursive --summarize --human-readable
    Total Objects: 38031
    Total Size: 74.6 GiB

## Create a 175 GB volume

## Download images, pipelines and load data files to AssayDev machine

E:
aws s3 sync s3://cellpainting-gallery/cpg0020-varchamp/broad/images/2024_12_09_Batch_11/ images\2024_12_09_Batch_11\
aws s3 sync s3://cellpainting-gallery/cpg0020-varchamp/broad/images/2024_12_09_Batch_12/ images\2024_12_09_Batch_12\

aws s3 sync s3://imaging-platform-ssf/projects/cpg0020-varchamp/workspace/load_data_csv/ workspace\load_data_csv\

aws s3 sync s3://cellpainting-gallery/cpg0020-varchamp/broad/workspace/pipelines/2024_10_28_Batch_9/ workspace\pipelines\2024_12_09_Batch_11\

## Edit load data files

`/home/ubuntu/bucket/cpg0020-varchamp/broad/` --> `E:\`
`/` --> `\`

## Run assay DEV
- Since it was only 2 plates per pipeline, I run it on the assaydev machine using regular CellProfiler instead of DCP

- I tried my best but the empty wells like L11-12 and M11-12 still get some huge 'cell' objects detected. They have higher bckd for some reason and I can't set a higher min for the ID_Secondary threshold without messing the detection of the other cells. This is worse on the widefield
- I added an additional filter for secondary objects to get rid of those on the widefield pipeline
- It's better but there are still some huge objects like that. I decide to live with that and move on.

## Upload pipelines and montage

aws s3 sync E:\\workspace\pipelines\ s3://imaging-platform-ssf/projects/cpg0020-varchamp/workspace/pipelines/2024_12_09_Batch_11/
aws s3 sync E:\\workspace\pipelines\ s3://imaging-platform-ssf/projects/cpg0020-varchamp/workspace/pipelines/2024_12_09_Batch_12/

aws s3 sync E:\\assaydev\ s3://imaging-platform-ssf/projects/cpg0020-varchamp/workspace/assaydev/

## Delete volume --> DONE!

=========================================
# ANALYSIS
=========================================

pyenv shell 3.8.13
cd efs/cpg0020-varchamp/workspace/software/Distributed-CellProfiler/
nano config.py

python3 run.py setup

PROJECT_NAME=cpg0020-varchamp
BUCKET=imaging-platform-ssf
BATCH_ID=2024_12_09_Batch_11
BATCH_ID=2024_12_09_Batch_12

python run_batch_general.py analysis cpg0020-varchamp 2024_12_09_Batch_11 "2024-12-09_B11A1R1" \
--source broad \
--path-style cpg \
--pipeline analysis_confocal.cppipe \
--pipeline-path projects/cpg0020-varchamp/workspace/pipelines/2024_12_09_Batch_11/ \
--datafile-path projects/cpg0020-varchamp/workspace/load_data_csv/2024_12_09_Batch_11/

python run_batch_general.py analysis cpg0020-varchamp 2024_12_09_Batch_12 "2024-12-09_B12A1R2" \
--source broad \
--path-style cpg \
--pipeline analysis_confocal.cppipe \
--pipeline-path projects/cpg0020-varchamp/workspace/pipelines/2024_12_09_Batch_11/ \
--datafile-path projects/cpg0020-varchamp/workspace/load_data_csv/2024_12_09_Batch_12/

python run_batch_general.py analysis cpg0020-varchamp 2024_12_09_Batch_11 "2024-12-09_B11A1R1_widefield" \
--source broad \
--path-style cpg \
--pipeline analysis_widefield.cppipe \
--pipeline-path projects/cpg0020-varchamp/workspace/pipelines/2024_12_09_Batch_11/ \
--datafile-path projects/cpg0020-varchamp/workspace/load_data_csv/2024_12_09_Batch_11/

python run_batch_general.py analysis cpg0020-varchamp 2024_12_09_Batch_12 "2024-12-09_B12A1R2_widefield" \
--source broad \
--path-style cpg \
--pipeline analysis_widefield.cppipe \
--pipeline-path projects/cpg0020-varchamp/workspace/pipelines/2024_12_09_Batch_11/ \
--datafile-path projects/cpg0020-varchamp/workspace/load_data_csv/2024_12_09_Batch_12/

    -->13824 messages

## Start Spot Fleet
python3 run.py startCluster files/Fleet.json
python run.py monitor files/cpg0020-varchamp_AnalysisSpotFleetRequestId.json

=========================================
# PREP FOR BACKENDS
=========================================

### Calculate total size of analysis files

aws s3 ls s3://cellpainting-gallery/cpg0020-varchamp/broad/workspace/analysis/2024_12_09_Batch_11/ --human-readable --summarize --recursive | grep Total
    Total Objects: 55232
    Total Size: 87.9 GiB

aws s3 ls s3://cellpainting-gallery/cpg0020-varchamp/broad/workspace/analysis/2024_12_09_Batch_12/ --human-readable --summarize --recursive | grep Total
    Total Objects: 55288
    Total Size: 91.8 GiB

- I create a 400 GB volume and process 1 batch at a time (/dev/sde)

## Login to Backends and set up
lsblk
    NAME     MAJ:MIN RM  SIZE RO TYPE MOUNTPOINT
    loop0      7:0    0 25.2M  1 loop /snap/amazon-ssm-agent/7993
    loop1      7:1    0 44.3M  1 loop /snap/snapd/23258
    loop2      7:2    0 26.3M  1 loop /snap/amazon-ssm-agent/9881
    loop3      7:3    0 55.4M  1 loop /snap/core18/2855
    loop4      7:4    0 73.9M  1 loop /snap/core22/1722
    loop5      7:5    0 55.4M  1 loop /snap/core18/2846
    loop6      7:6    0 44.4M  1 loop /snap/snapd/23545
    loop7      7:7    0 73.9M  1 loop /snap/core22/1748
    xvda     202:0    0   40G  0 disk 
    ├─xvda1  202:1    0 39.9G  0 part /
    ├─xvda14 202:14   0    4M  0 part 
    └─xvda15 202:15   0  106M  0 part /boot/efi
    xvde     202:64   0  400G  0 disk 

sudo file -s /dev/xvde
    /dev/xvde: data

sudo mkfs -t ext4 /dev/xvde
    mke2fs 1.44.1 (24-Mar-2018)
    Creating filesystem with 104857600 4k blocks and 26214400 inodes
    Filesystem UUID: 1f4efca8-676c-42d0-a7de-68c28dc8e8ab
    Superblock backups stored on blocks: 
            32768, 98304, 163840, 229376, 294912, 819200, 884736, 1605632, 2654208, 
            4096000, 7962624, 11239424, 20480000, 23887872, 71663616, 78675968, 
            102400000

    Allocating group tables: done                            
    Writing inode tables: done                            
    Creating journal (262144 blocks): done
    Writing superblocks and filesystem accounting information: done

sudo mount /dev/xvde /home/ubuntu/ebs_tmp
sudo chmod 777 ~/ebs_tmp/
lsblk
    NAME     MAJ:MIN RM  SIZE RO TYPE MOUNTPOINT
    loop0      7:0    0 25.2M  1 loop /snap/amazon-ssm-agent/7993
    loop1      7:1    0 44.3M  1 loop /snap/snapd/23258
    loop2      7:2    0 26.3M  1 loop /snap/amazon-ssm-agent/9881
    loop3      7:3    0 55.4M  1 loop /snap/core18/2855
    loop4      7:4    0 73.9M  1 loop /snap/core22/1722
    loop5      7:5    0 55.4M  1 loop /snap/core18/2846
    loop6      7:6    0 44.4M  1 loop /snap/snapd/23545
    loop7      7:7    0 73.9M  1 loop /snap/core22/1748
    xvda     202:0    0   40G  0 disk 
    ├─xvda1  202:1    0 39.9G  0 part /
    ├─xvda14 202:14   0    4M  0 part 
    └─xvda15 202:15   0  106M  0 part /boot/efi
    xvde     202:64   0  400G  0 disk /home/ubuntu/ebs_tmp

pyenv shell 3.8.13

PROJECT_NAME=cpg0020-varchamp
BATCH_ID=2024_12_09_Batch_12
BUCKET=cellpainting-gallery
MAXPROCS=7 

## Get list of plates and define plate variable
mkdir -p ~/ebs_tmp/cpg0020-varchamp/workspace/scratch/2024_12_09_Batch_12/
PLATES=$(readlink -f ~/ebs_tmp/cpg0020-varchamp/workspace/scratch/2024_12_09_Batch_12/plates_to_process.txt)
aws s3 ls s3://cellpainting-gallery/cpg0020-varchamp/broad/workspace/analysis/2024_12_09_Batch_12/ |cut -d " " -f29 | cut -d "/" -f1 >> ${PLATES}

nano $PLATES
    2024-12-09_B12A1R2
    2024-12-09_B12A1R2_widefield

## Install pycytominer
mkdir -p ~/ebs_tmp/${PROJECT_NAME}/workspace/software
cd ~/ebs_tmp/${PROJECT_NAME}/workspace/software
if [ -d pycytominer ]; then rm -rf pycytominer; fi
git clone https://github.com/cytomining/pycytominer.git
cd pycytominer
#python3 -m pip install -e . ---> `fails bc Pycytominer no longer supports PYthon 3.8.13`

pip install pycytominer==1.2.0

## Make backends
cd ~/ebs_tmp/${PROJECT_NAME}/workspace/software/pycytominer/
mkdir -p  ../../log/${BATCH_ID}/
parallel \
--max-procs ${MAXPROCS} \
--ungroup \
--eta \
--joblog ../../log/${BATCH_ID}/collate.log \
--results ../../log/${BATCH_ID}/collate \
--files \
--keep-order \
python3 pycytominer/cyto_utils/collate_cmd.py ${BATCH_ID} pycytominer/cyto_utils/database_config/ingest_config.ini {1} \
--image-feature-categories "Granularity,Texture,ImageQuality,Count,Threshold,Intensity" \
--tmp-dir ~/ebs_tmp \
--aws-remote=s3://${BUCKET}/${PROJECT_NAME}/broad/workspace :::: ${PLATES} <-- `Remove this flag, as the upload to SPG does not fully work yet`

#### sqlite files are in `ebs_tmp/backend/2024_12_09_Batch_12/` and NOT in `ebs_tmp/cpg0020-varchamp/workspace/backend/2024_12_09_Batch_12` (which is full of empty folders with plate names).

#### SOLUTION --> move the sqlite file to where to script is expecting them:

mv ~/ebs_tmp/backend/2024_12_09_Batch_12/* ~/ebs_tmp/cpg0020-varchamp/workspace/backend/2024_12_09_Batch_12/

rm -rf ~/ebs_tmp/backend/2024_12_09_Batch_12/

ls ~/ebs_tmp/cpg0020-varchamp/workspace/backend/2024_12_09_Batch_12/
    2024-12-09_B12A1R2  2024-12-09_B12A1R2_widefield

du -sh ~/ebs_tmp/cpg0020-varchamp/workspace/backend/2024_12_09_Batch_12/
    23G     /home/ubuntu/ebs_tmp/cpg0020-varchamp/workspace/backend/2024_12_09_Batch_12/


## Run backend again with the --collate-only flag --> without the --aws-remote flag!
cd ~/ebs_tmp/${PROJECT_NAME}/workspace/software/pycytominer/
mkdir -p  ../../log/${BATCH_ID}/
parallel \
--max-procs ${MAXPROCS} \
--ungroup \
--eta \
--joblog ../../log/${BATCH_ID}/collate.log \
--results ../../log/${BATCH_ID}/collate \
--files \
--keep-order \
python3 pycytominer/cyto_utils/collate_cmd.py ${BATCH_ID} pycytominer/cyto_utils/database_config/ingest_config.ini {1} \
--image-feature-categories "Granularity,Texture,Count,Threshold" \
--tmp-dir ~/ebs_tmp \
--aggregate-only :::: ${PLATES}

`ERROR` --> ValueError: Some of the input image features are not present in the image table.
--> likely bc ImageQuality and Intensity were not present as an image feature
--> Remove ImageQuality and Intensity from the image-features-categories

### Check progress
PLATE=2024-12-09_B12A1R2
PROJECT_NAME=cpg0020-varchamp
BATCH_ID=2024_12_09_Batch_12
BUCKET=cellpainting-gallery
MAXPROCS=7 

cat ~/ebs_tmp/${PROJECT_NAME}/workspace/log/${BATCH_ID}/collate/1/2024-12-09_B12A1R2/stdout |tail
cat ~/ebs_tmp/${PROJECT_NAME}/workspace/log/${BATCH_ID}/collate/1/${PLATE}/stderr
ls -lahR ~/ebs_tmp/backend/ | grep sqlite

### Check that backends finished correctly
ls ~/ebs_tmp/cpg0020-varchamp/workspace/backend/2024_12_09_Batch_12/2024-12-09_B12A1R2/
    2024-12-09_B12A1R2.csv  2024-12-09_B12A1R2.sqlite

# BACKENDS DON'T WORK END-TO-END WITH UPLOAD TO THE CPG! --> need to copy SQLITES and CSVs manually to CPG

## Upload Backend to S3
aws s3 sync ~/ebs_tmp/cpg0020-varchamp/workspace/backend/2024_12_09_Batch_12/ s3://imaging-platform-ssf/cpg0020-varchamp/broad/workspace/backend/2024_12_09_Batch_12/


## Download Backend to local machine
aws s3 sync s3://imaging-platform-ssf/cpg0020-varchamp/broad/workspace/backend/2024_12_09_Batch_12/ /Users/emigliet/Downloads/backend/2024_12_09_Batch_12/

## Upload to CPG directly
aws s3 cp --recursive /Users/emigliet/Downloads/backend/2024_12_09_Batch_12/ s3://cellpainting-gallery/cpg0020-varchamp/broad/workspace/backend/2024_12_09_Batch_12/ --profile cpg-access-role


## Check that transfer was succesful
aws s3 ls s3://cellpainting-gallery/cpg0020-varchamp/broad/workspace/backend/2024_12_09_Batch_12/ --recursive --summarize --human-readable | grep Total
    Total Objects: 5
    Total Size: 22.4 GiB


## Make metadata and upload to S3
- I used `B11A1R1_P1` and `B12A1R2_P1` as platemap names

aws s3 sync /Users/emigliet/Documents/GitHub/emiglietta_projects/2024_Varchamp/Batch_11_12/metadata s3://imaging-platform-ssf/cpg0020-varchamp/broad/workspace/metadata/2024_12_09_Batch_12/ --exclude ".DS_Store"


================
## Make profiles
================

### On Bakcends:

tmux new -s profiles

BUCKET=imaging-platform-ssf
PROJECT_NAME=cpg0020-varchamp
MAXPROCS=7 
ORG=broadinstitute
USER=emiglietta
DATA=2021_09_01_VarChAMP-data

#### Download Backend files:

aws s3 sync s3://imaging-platform-ssf/cpg0020-varchamp/broad/workspace/backend/2024_12_09_Batch_12/ ~/work/projects/cpg0020-varchamp/workspace/backend/2024_12_09_Batch_12 --exclude="*" --include="*.csv"

#### Repos are already cloned and welded. Update submodules, just in case
cd ~/work/projects/${PROJECT_NAME}/workspace/software/${DATA}
git submodule update --init --recursive

#### Set up the environment
cp profiling-recipe_EM/environment.yml .
conda env create --yes --file environment.yml

conda activate profiling

#### Set up DVC to store large files in S3
cd ~/work/projects/${PROJECT_NAME}/workspace/software/${DATA}
dvc init -f
    ModuleNotFoundError: No module named 'funcy.py3'
    --> solve by running `pip install funcy==1.18`
dvc remote add -d S3storage s3://cellpainting-gallery/${PROJECT_NAME}/broad/workspace/software/${DATA}_DVC
dvc remote modify S3storage profile cpg-access-role
dvc remote modify S3storage acl 'bucket-owner-full-control'
git add .dvc/.gitignore .dvc/config
git commit -m "Setup DVC"

#### Download the load_data_CSVs
aws s3 sync s3://imaging-platform-ssf/cpg0020-varchamp/broad/workspace/load_data_csv/2024_12_09_Batch_12/ load_data_csv/2024_12_09_Batch_12
gzip -r load_data_csv/2024_12_09_Batch_12

#### Download the metadata files
aws s3 sync s3://imaging-platform-ssf/cpg0020-varchamp/broad/workspace/metadata/2024_12_09_Batch_12/ metadata/platemaps/2024_12_09_Batch_12

#### Make new config file 
cp profiling-recipe_EM/config_template.yml config_files/config_batch_12.yml
nano config_files/config_batch_12.yml
    (check settings with previous batches https://cellpainting-gallery.s3.amazonaws.com/index.html#cpg0020-varchamp/broad/workspace/config_files/)

==========================================================
---
pipeline: analysis
output_dir: profiles
platemap_well_column: Metadata_well_position
compartments:
  - cells
  - cytoplasm
  - nuclei
aggregate:
  perform: false
  plate_column: Metadata_Plate
  well_column: Metadata_Well
  method: median
  fields: all
  image_feature_categories:
    - Count
    - Intensity
annotate:
  perform: true
  well_column: Metadata_Well
  external :
    perform: false
    file: <metadata file name>
    merge_column: <Column to merge on>
normalize:
  perform: true
  method: mad_robustize
  features: infer
  mad_robustize_fudge_factor: 0
  image_features: true
  min_cells: 1
normalize_negcon:
  perform: false
  method: mad_robustize
  features: infer
  mad_robustize_fudge_factor: 0
  image_features: true
  min_cells: 1
feature_select:
  perform: true
  features: infer
  level: batch
  gct: true
  image_features: true
  operations:
    - variance_threshold
    - correlation_threshold
    - drop_na_columns
    - blocklist
  min_cells: 1
feature_select_negcon:
  perform: false
  features: infer
  level: batch
  gct: false
  image_features: true
  operations:
    - variance_threshold
    - correlation_threshold
    - drop_na_columns
    - blocklist
  min_cells: 1
quality_control:
  perform: true
  summary:
    perform: true
    row: Metadata_Row
    column: Metadata_Col
  heatmap:
    perform : true
options:
  compression: gzip
  float_format: "%.5g"
  samples: all
---
batch: 2024_12_09_Batch_12
plates:
  - name: 2024-12-09_B12A1R2
    process: true
  - name: 2024-12-09_B12A1R2_widefield
    process: true
process: true
========================================

#### Set up profiles

BATCH_ID=2024_12_09_Batch_12

mkdir -p profiles/${BATCH_ID}
find ../../backend/${BATCH_ID}/ -type f -name "*.csv" -exec profiling-recipe/scripts/csv2gz.py {} \;
rsync -arzv --include="*/" --include="*.gz" --exclude "*" ../../backend/${BATCH_ID}/ profiles/${BATCH_ID}/
    2024-12-09_B12A1R2/2024-12-09_B12A1R2.csv.gz
    2024-12-09_B12A1R2_widefield/2024-12-09_B12A1R2_widefield.csv.gz

    sent 12,781,755 bytes  received 60 bytes  8,521,210.00 bytes/sec
    total size is 12,780,563  speedup is 1.00


### Run the profiling workflow

python profiling-recipe_EM/profiles/profiling_pipeline.py  --config config_files/config_batch_12.yml
    Now processing... batch: 2024_12_09_Batch_12
    Now annotating... plate: 2024-12-09_B12A1R2
    Now normalizing... plate: 2024-12-09_B12A1R2
    Now annotating... plate: 2024-12-09_B12A1R2_widefield
    Now normalizing... plate: 2024-12-09_B12A1R2_widefield
    Now feature selecting... level: batch
    Now generating summary
    /home/ubuntu/work/projects/cpg0020-varchamp/workspace/software/2021_09_01_VarChAMP-data/profiling-recipe_EM/profiles/profile.py:468: FutureWarning: The frame.append method is deprecated and will be removed from pandas in a future version. Use pandas.concat instead.
    summary = summary.append(
    /home/ubuntu/work/projects/cpg0020-varchamp/workspace/software/2021_09_01_VarChAMP-data/profiling-recipe_EM/profiles/profile.py:468: FutureWarning: The frame.append method is deprecated and will be removed from pandas in a future version. Use pandas.concat instead.
    summary = summary.append(
    Now generating heatmaps

#### Push files to DVC and GitHub
dvc add profiles/${BATCH_ID}
dvc push
git add profiles/${BATCH_ID}.dvc profiles/.gitignore
git commit -m 'add profiles'
git add *
git commit -m 'add files made in profiling'
git push

#### Push files to CPG

`Profiles`
aws s3 cp --recursive profiles/2024_12_09_Batch_12/ s3://cellpainting-gallery/cpg0020-varchamp/broad/workspace/profiles/2024_12_09_Batch_12/ --profile cpg-access-role

`Quality_control`
aws s3 cp --recursive quality_control/heatmap/2024_12_09_Batch_12/ s3://cellpainting-gallery/cpg0020-varchamp/broad/workspace/quality_control/heatmap/2024_12_09_Batch_12/ --profile cpg-access-role

`AssayDev`
aws s3 cp --recursive s3://imaging-platform-ssf/cpg0020-varchamp/broad/workspace/assaydev/montages/2024_12_09_Batch_12/ s3://cellpainting-gallery/cpg0020-varchamp/broad/workspace/assaydev/montages/2024_12_09_Batch_12/ --profile cpg-access-role

`Load_data_csv_orig`
aws s3 cp --recursive load_data_csv/2024_12_09_Batch_12/ s3://cellpainting-gallery/cpg0020-varchamp/broad/workspace/load_data_csv_orig/2024_12_09_Batch_12/ --profile cpg-access-role

`Metadata`
aws s3 cp --recursive metadata/platemaps/2024_12_09_Batch_12/ s3://cellpainting-gallery/cpg0020-varchamp/broad/workspace/metadata/platemaps/2024_12_09_Batch_12/  --profile cpg-access-role

`Pipelines`
aws s3 cp --recursive s3://imaging-platform-ssf/cpg0020-varchamp/broad/workspace/pipelines/2024_12_09_Batch_12/ s3://cellpainting-gallery/cpg0020-varchamp/broad/workspace/pipelines/2024_12_09_Batch_12/  --profile cpg-access-role



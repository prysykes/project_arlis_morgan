import pandas as pd
import boto3, base64, os
import uuid
from botocore.exceptions import ClientError
from datetime import datetime

# Create your views here.

cred_pad = '/Users/prynet/Documents/aws_cred/emeka_accessKeys.csv'
df = pd.read_csv(cred_pad)#print(df.columns)
access_key_id = df.loc[df.index[0], 'Access key ID'] #df.index[0] returns first row, second argument is the column name 
secret_access_key = df.loc[df.index[0], 'Secret access key']
region_name = 'us-east-1'

session = boto3.Session(
    aws_access_key_id=access_key_id,
    aws_secret_access_key=secret_access_key,
    region_name=region_name
)

iam = session.client('iam')
sagemaker = session.client('sagemaker')
s3_client = session.client('s3')
s3_bucket = 'mlwb-trainer-app'


def create_iam_role(user, role_name):
    try:
        role = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument='{"Version": "2012-10-17","Statement": [{"Effect": "Allow","Action": "sts:AssumeRole","Principal": {"Service": "sagemaker.amazonaws.com"}}]}',
            Description="SageMaker execution role for user " + str(user),
            MaxSessionDuration=3600
        )
        arn = role["Role"]["Arn"]
        return arn
    except ClientError as e:
        if e.response['Error']['Code'] == 'EntityAlreadyExists':
            response = iam.get_role(RoleName=role_name)
            arn = response['Role']['Arn']
            print("see exist arn", arn)
            return arn
    except Exception as e:
        print(str(e))


def create_notebook_instance(instance_name, instance_type, lifecycle_config_name, role_arn):
    """
    Creates a new Amazon SageMaker notebook instance with the specified parameters.

    :param instance_name: The name to assign to the new notebook instance.
    :param instance_type: The type of EC2 instance to use for the notebook instance (e.g. 'ml.t2.medium').
    :param lifecycle_config_name: The name of the lifecycle configuration to associate with the notebook instance.
    :param role_arn: The ARN of the IAM role to use for the notebook instance.
    :return: The response from the CreateNotebookInstance API call, or a string error message if an error occurs.
    """

    try:
        
        # Set up the CreateNotebookInstance request parameters
        create_params = {
            'NotebookInstanceName': instance_name,
            'InstanceType': instance_type,
            'LifecycleConfigName': lifecycle_config_name,
            'RoleArn': role_arn
        }

        # Send the CreateNotebookInstance request and return the response
        response = sagemaker.create_notebook_instance(**create_params)
        return response

    except Exception as e:
        error_message = f"Error creating notebook instance: {str(e)}"
        return error_message


def check_notebook_instance(instance_name):
    try:
        response = sagemaker.describe_notebook_instance(
            NotebookInstanceName=instance_name
        )
        status = response["NotebookInstanceStatus"]
        return status
    except Exception as e:
        return str(e)

def get_iam_role(role_name):
    try:
        response = iam.get_role(
            RoleName=role_name
        )
        arn = response["Role"]["Arn"]
        return arn
    except Exception as e:
        return str(e)

def get_notebook_instance(instance_name):
    try:
        response = sagemaker.describe_notebook_instance(
            NotebookInstanceName=instance_name
        )
        return response
    except Exception as e:
        return str(e)

def get_notebook_instance_url(instance_name):
    try:
        response = sagemaker.describe_notebook_instance(
            NotebookInstanceName=instance_name
        )
        url = response["Url"]
        return url
    except Exception as e:
        return str(e)

def delete_notebook_instance(instance_name):
    try:
        response = sagemaker.delete_notebook_instance(
            NotebookInstanceName=instance_name
        )
        return "Notebook instance deleted successfully."
    except Exception as e:
        return str(e)

def get_notebook_instance_jupyterlab_url(instance_name):
    print("fetching JupyterLab URL.....")
    try:
        response = sagemaker.create_presigned_notebook_instance_url(
        NotebookInstanceName=instance_name,
        SessionExpirationDurationInSeconds=3600,
        # AdditionalParamaters={
        #     'View': 'JupyterLab'
        # }
    )
        url = response["AuthorizedUrl"]
        return url
    except Exception as e:
        return str(e)
        
def delete_notebook_instance(instance_name):
    try:
        response = sagemaker.delete_notebook_instance(
            NotebookInstanceName=instance_name
        )
        return "Notebook instance deleted successfully."
    except Exception as e:
        return str(e)

def stop_notebook_instance(instance_name):
    try:
        response = sagemaker.stop_notebook_instance(
            NotebookInstanceName=instance_name
        )
        status = response["NotebookInstanceStatus"]
        return status
    except Exception as e:
        return str(e)

import uuid

def upload_to_s3(file, user, filename, bucket):
    folder_name = f'{user}'
    object_key = f'{folder_name}/{filename}'

    # Print the file size before uploading
    print(f"File size before upload: {file.size}")

    try:
        s3_client.upload_fileobj(file, bucket, object_key)
    except Exception as e:
        print(f"Error during upload: {str(e)}")
        return False, str(e)

    return True, ''



def create_lifecycle_configs(user):
    sagemaker_instance_dir = f"/home/ec2-user/SageMaker/{user}"
    bucket_name = s3_bucket
    
    # Create scripts
    on_create_script = f"#!/bin/bash\n\naws s3 sync {sagemaker_instance_dir} s3://{bucket_name}/sagemaker/ --delete\n"
    on_start_script = f"#!/bin/bash\n\naws s3 sync s3://{bucket_name}/sagemaker/ {sagemaker_instance_dir} --delete\n"
    # on_stop_script = f"#!/bin/bash\n\naws s3 sync {sagemaker_instance_dir} s3://{bucket_name}/sagemaker/ --delete\n"
    
    # Encode scripts
    on_create_script_encoded = base64.b64encode(on_create_script.encode('ascii')).decode('ascii')
    on_start_script_encoded = base64.b64encode(on_start_script.encode('ascii')).decode('ascii')
    # on_stop_script_encoded = base64.b64encode(on_stop_script.encode('ascii')).decode('ascii')
    
    # Upload scripts to S3
    current_time = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    on_create_key = f"lifecycleconfig/on-create-{current_time}.sh"
    on_start_key = f"lifecycleconfig/on-start-{current_time}.sh"
    # on_stop_key = f"lifecycleconfig/on-stop-{current_time}.sh"
    
    s3_client.put_object(Bucket=bucket_name, Key=on_create_key, Body=on_create_script_encoded)
    s3_client.put_object(Bucket=bucket_name, Key=on_start_key, Body=on_start_script_encoded)
    # s3_client.put_object(Bucket=bucket_name, Key=on_stop_key, Body=on_stop_script_encoded)
    
    # Return S3 keys for lifecycle configurations
    return on_create_key, on_start_key


def upload_folder_to_s3(bucket_name, folder_path):
    # Get the name of the root directory
    root_dir = os.path.basename(folder_path)

    # Upload the folder and its contents to S3
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            local_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_path, folder_path)
            s3_path = os.path.join(root_dir, relative_path).replace('\\', '/')
            s3_path = s3_path.replace('\\', '/')  # Replace backslashes with forward slashes
            s3_client.upload_file(local_path, bucket_name, s3_path)


def create_lifecycle_config(script_path, lc_config_name):
    """
    Create a lifecycle configuration for a SageMaker notebook instance using a script saved locally.

    :param script_path: Path to the lifecycle configuration script file
    :param lc_config_name: Name of the lifecycle configuration to create
    """

    sm_client = sagemaker

    # Check if a lifecycle configuration already exists with the specified name
    try:
        sm_client.describe_notebook_instance_lifecycle_config(
            NotebookInstanceLifecycleConfigName=lc_config_name
        )

        # If the describe call succeeds, the lifecycle config exists
        print(f"Lifecycle configuration '{lc_config_name}' already exists. Deleting...")

        # Delete the existing lifecycle configuration
        sm_client.delete_notebook_instance_lifecycle_config(
            NotebookInstanceLifecycleConfigName=lc_config_name
        )

        print(f"Lifecycle configuration '{lc_config_name}' deleted.")
    except sm_client.exceptions.ResourceNotFound:
        # If the describe call fails with a ResourceNotFound exception, the lifecycle config doesn't exist
        pass
    except Exception as e:
        print("***", str(e))
        

    # Read the script content
    with open(script_path, 'r') as f:
        script_content = f.read()

    # Encode the script content as base64
    base64_encoded = base64.b64encode(script_content.encode('utf-8')).decode('utf-8')

    # Create the new lifecycle configuration
    sm_client.create_notebook_instance_lifecycle_config(
        NotebookInstanceLifecycleConfigName=lc_config_name,
        OnCreate=[{
            'Content': base64_encoded
        }]
    )

    print(f"Lifecycle configuration '{lc_config_name}' created.")



def delete_s3_directory(bucket_name, directory_name):
    prefix = directory_name + '/'
    try:
        response = s3_client.list_objects(Bucket=bucket_name, Prefix=prefix)

        if 'Contents' in response:
            delete_keys = [{'Key': obj['Key']} for obj in response['Contents']]
            s3_client.delete_objects(Bucket=bucket_name, Delete={'Objects': delete_keys})
    except ClientError as e:
        print(f'Error deleting directory {directory_name} from S3 bucket {bucket_name}: {e}')



def download_dataset(bucket_name, s3_object_key, dataset_dir):


    # Download the dataset from S3
    s3_client.download_file(bucket_name, s3_object_key, f"{dataset_dir}")

    print("Dataset downloaded to:", dataset_dir)
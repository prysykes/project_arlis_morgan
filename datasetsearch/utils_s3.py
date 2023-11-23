import boto3
import os
import glob


client = boto3.client('s3')

#response = client.list_buckets()
# bucket= 'mlwb-datasets'
# file_name = "datasetsearch/tests.py"
# parent_dir = os.getcwd()
# static_folder = os.path.join(parent_dir, 'static')
# kaggle_datasets_folder = os.path.join(static_folder, 'kaggle_dataset')
# user = 'emmy'
# print(os.listdir(kaggle_datasets_folder))

def retrieve_files_from_userS3(user, bucket):
    context = {'owner': 'Kaggle',
        'kaggle': []}
    s3 = boto3.resource('s3')

    
    target_bucket = s3.Bucket(bucket)
    counter = 0
    for obj in target_bucket.objects.filter(Prefix=user):
        #prefix allows you to filter the list of 
        # items in the bucket based on folders in the bucket
        #in this case user
        current_obj = obj.key
        current_obj_split = current_obj.split("/")
        
        context['kaggle'].append(current_obj_split[1]) 
        # context[counter] = current_obj_split[1]
       
        counter += 1
    
    return context


#print(response)




def get_downloaded_dtset_and_mv2_s3(user, kaggle_datasets_folder, bucket, datasets, object_name=None, args=None):
    
    #object_name = os.path.join(user, file_base_name)
    #len(glob.glob(f"{download_fullpath_user}/*")) != 0:
    #user_files_path = os.path.join(kaggle_datasets_folder, user)
    user_files_path = os.path.join(kaggle_datasets_folder, user)
    user_file_list = glob.glob(f"{user_files_path}/*")
    print("user_file_list:", user_file_list)
    #user_file_list = os.listdir(user_files_path)
    
    for file in user_file_list:
        
        file_name = file
        file_name_wo_path = os.path.basename(file)
        object_name = f"{user}/{file_name_wo_path}" 
        response = client.upload_file(file_name, bucket, object_name, ExtraArgs=args)
        
        os.remove(file_name)#removes the file from the local directory
    return datasets
#get_downloaded_dtset_and_mv2_s3(user, kaggle_datasets_folder, bucket)

def delete_dataset_from_s3_bucket(user, bucket):
    s3 = boto3.resource('s3')
    target_bucket = s3.Bucket(bucket)

    for obj in target_bucket.objects.filter(Prefix=user):
        print(obj)
import pandas as pd
import os
import posixpath
import subprocess
import glob
import zipfile


import boto3

from .utils_s3 import get_downloaded_dtset_and_mv2_s3



client = boto3.client('s3')

#response = client.list_buckets()
bucket= 'mlwb-datasets'
file_name = "datasetsearch/tests.py"
parent_dir = os.getcwd()
static_folder = os.path.join(parent_dir, 'static')


#print(os.listdir(kaggle_datasets_folder))


download_path = os.getcwd()
#kaggle_dataset = "kaggle_dataset"
path_to_static = os.path.join(download_path, 'static')
download_fullpath = os.path.join(path_to_static, 'kaggle_dataset')

os.environ['KAGGLE_USERNAME'] = 'chukwuemekaduru'
os.environ['KAGGLE_KEY'] = '31d5520d7619e481490ba2993da9742c'


def search_kaggle(search_term):
    command = ['kaggle', 'datasets', 'list', '-s']
    # kaggle defined way to interact with its API
    command.append(search_term)
    # capture=True stops it from outputing data to the cli
    pre_search_results = subprocess.run(
        command, capture_output=True, encoding="ISO-8859-1")
    # changed the default encoding from utf-8 to iso-8859-1 to stop
    # 'utf-8' codec can't decode byte 0xe9 in position 823: invalid continuation byte  error
    # print(pre_search_results)
    # decode is needed to convert to string because std out output the data as byte.
    search_results = list(pre_search_results.stdout.splitlines())
    #print("getting type", search_results)
    search_results.pop(1)

    return search_results


def read_directory(dir):
    # reads the user directory and extracts all zip files
    # uci datasets comes as zip files
    if glob.glob(f"{dir}/*.zip") != 0:
        # only searches for zip files
        all_files_zip = glob.glob(f"{dir}/*.zip")
        latest_files_without_path = os.path.basename(all_files_zip[0])

        with zipfile.ZipFile(latest_files_without_path, 'r') as zip_dataset:
            zip_dataset.extractall(os.getcwd())
        # add the full path to the zip file then deletes it
        zip_file_to_delete = os.path.join(dir, latest_files_without_path)
        os.remove(zip_file_to_delete)

        return zip_file_to_delete


def retrieve_datasets_kaggle(user):
    user = str(user)
    
    download_fullpath_user = os.path.join(download_fullpath, user)
    os.chdir(download_fullpath)
    os.chdir(download_fullpath_user)
    short_path = f'/static/kaggle_dataset/{user}'
    context = {}

    csv_files, xlsx_files, audio_files, img_files, text_files = (
        [] for i in range(5))  # creating multiple list to hold files
    # check if the directory is empty
    if len(glob.glob(f"{download_fullpath_user}/*")) != 0:
        everyevery = glob.glob(f"{download_fullpath_user}/*")

        if (glob.glob(f"{download_fullpath_user}/*.csv")) != 0:
            #selects on the csv file
            print("make I know length", len(
                glob.glob(f"{download_fullpath_user}/*.csv")))
            files_c = glob.glob(f"{download_fullpath_user}/*.csv")
            for file in files_c:
                file_name = os.path.basename(file)
                print("file Nam: ", file_name)
                print("filooo", file[file.find('static'):])
                href = file[file.find('static'):]
                csv_files.insert(0, {file_name: href})
                # csv_files.append({file_name: href})
                print("CSV FILES: ", csv_files)
            context['csv_files'] = csv_files
        # if glob.glob(f"{download_fullpath_user}/*.xlsx") != 0:
        #     print("there is xlsx file")
        #     files_x = glob.glob(f"{download_fullpath_user}/*.xlsx")
        #     for file in files_x:
        #         xlsx_files.append(file)
        #     context['xlsx_files'] = xlsx_files
        # if glob.glob(f"{download_fullpath_user}/*.wav") != 0:
        #     print("there is csv wav")
        #     files_w = glob.glob(f"{download_fullpath_user}/*.wav")
        #     for file in files_w:
        #         audio_files.append(file)
        #     context['audio_files'] = audio_files
        # if glob.glob(f"{download_fullpath_user}/*.png") != 0:
        #     print("there is csv png")
        #     files_p = glob.glob(f"{download_fullpath_user}/*.png")
        #     for file in files_p:
        #         img_files.append(file)
        #     context['img_files'] = img_files
        # if glob.glob(f"{download_fullpath_user}/*.txt") != 0:
        #     print("there is csv text")
        #     files_t = glob.glob(f"{download_fullpath_user}/*.txt")
        #     for file in files_t:
        #         text_files.append(file)
        #     context['text_files'] = text_files
    return context


def download_dataset_kagle(term, user):
    kaggle_datasets_folder = os.path.join(static_folder, 'kaggle_dataset')
    bucket= 'mlwb-datasets'
    user = str(user)
    os.chdir(download_fullpath)
    try:
        os.mkdir(user)
    except FileExistsError:
        download_fullpath_user = os.path.join(download_fullpath, user)
    #subprocess.Popen('ls')

    os.chdir(download_fullpath_user)
    # subprocess.Popen('ls')
    command = ['kaggle', 'datasets', 'download', '-d', str(term)]
    subprocess.run(command)
    read_directory(download_fullpath_user)
    # print(latest_files)
    datasets =  retrieve_datasets_kaggle(user)
    """
        logic to move downloaded file should go into this porttion once a file is downloaded
    """
    

    os.chdir(download_path)
    #get_downloaded_dtset_and_mv2_s3(user, kaggle_datasets_folder, bucket)
    get_downloaded_dtset_and_mv2_s3(user, kaggle_datasets_folder, bucket, datasets)

    # returns the OS environment to the base dir
    # else UCI chng dir will raise file error
    return datasets

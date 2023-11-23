from ast import Continue
from importlib.resources import path
from multiprocessing import context
from django.contrib import messages
#browser handling and changing chrome default directory imports

import urllib
import requests


import pandas as pd
from bs4 import BeautifulSoup
import pickle
import re
import os
import posixpath
import json
import sys
import subprocess
import glob
import zipfile


# download_path = os.getcwd()
# kaggle_dataset = "kaggle_dataset"
# download_fullpath = os.path.join(download_path, kaggle_dataset)

parent_dir = os.getcwd()
uci_dataset = "uci_dataset"
path_to_static = os.path.join(parent_dir, 'static') 
download_full_path = os.path.join(path_to_static, 'uci_datasett')


def load_json():
    with open('static/uci_dataset.json', 'r') as jsonfile:
        dataset_rows = jsonfile.read()
        results = json.loads(dataset_rows)
        return results
"""
The commented functions below (save_uci_list and scrap_uci) will be handy in the second phase
"""

parent_directory = os.getcwd()

uci_dataset_url = "https://archive.ics.uci.edu/ml/datasets.php?format=&task=&att=&area=&numAtt=&numIns=&type=&sort=nameUp&view=list"

# sys.setrecursionlimit(1000000) 
def getHTMLdocument(url):
    response = requests.get(url)
    return response.text


html_ducument = getHTMLdocument(uci_dataset_url)


def save_uci_list(dataset_name, dataset_description):
    #current_dir = os.getcwd()
    
    results = {}
    # print(data_list)
    if os.path.basename(os.path.normpath(parent_dir)) != 'static':
        # os.basename strips of all trailing slashes
        # os.normpath returns the last part of the path
        os.chdir('static')
        print("changed to static")
    
    for i in range(0, len(dataset_name)):
        results[i] = list()
        results[i].append(str(dataset_name[i]))
        results[i].append(str(dataset_description[i]))
    
    # print(results)
    with open('uci_dataset.json', 'w') as f:
        json.dump(results, f)
    
        # for line in data_list:
        #     f.write(f"{line}\n")
    with open('uci_dataset.json', 'r') as rf:
        file_content = rf.read()
        result_to_render = json.loads(file_content)
   
    return result_to_render



def scrap_uci(search_key):
    links = list()
    links_two = list()
    soup = BeautifulSoup(html_ducument, 'html.parser')
    table = soup.find('table', attrs={'cellpadding': '3'})
    p_tags = table.find_all('p', attrs={'class': 'normal'})
    dataset_description = str(table.find_all('p', attrs={'class': 'normal'})).split(':')
    # print("description", dataset_description)
    p_tags_to_list = list(p_tags)
    for p_tag in p_tags_to_list:
        b_tag = p_tag.findChildren('b')
        if b_tag != []:
            links.append(b_tag[0])
    
    for i in range(0, len(dataset_description)):
        if i == 0:
            continue
        links_two.append("#"+dataset_description[i][0:dataset_description[i].find('<')])
        # hash above is to enable us split the dataset properly at the frontend
        # dataset_description[i].find('<') gets the index of < to enable us select the description
    
    results_from_scrap = save_uci_list(links, links_two)

    return results_from_scrap


def get_dataset_download_url(url):
    response = requests.get(url)
    return response.text

def get_download_dataset_url(link):
    response = requests.get(link)
    return response.text

# def read_directory(user_dir):
#     if glob.glob(f"{user_dir}/*.zip") != 0:
#         zip_files = glob.glob(f"{user_dir}/*.zip")
#         zip_file_without_path = os.path.basename(zip_files[0])
#         directory_name = zip_file_without_path.split('.')[0]
#         print("directory name;", directory_name)
#         with zipfile.ZipFile(zip_file_without_path, 'r') as zip_dataset:
#             directory = os.mkdir(directory_name)
#             zip_dataset.extractall(directory)
#         zip_file_to_delete = os.path.join(user_dir, zip_file_without_path)
#         os.remove(zip_file_to_delete)
#         return zip_file_without_path

def retrieve_dataset_uci(user):
    dir = download_full_path
    
    user = str(user)
    path_to_read = os.path.join(dir, user)
    #print("Path to read: ", path_to_read)
    os.chdir(path_to_read)
    context = {}
    csv_files, xlsx_files, audio_files, img_files, text_files = (
        [] for i in range(5)) # creating multiple list to hold files
    #print("length zip", len(glob.glob(f"{path_to_read}/*.zip")))
    if len(glob.glob(f"{path_to_read}/*")) != 0: # this check if the directory is empty
        if (glob.glob(f"{path_to_read}/*.csv")) != 0:
            file_c = glob.glob(f"{path_to_read}/*.csv")
            for file in file_c:
                print(file)
        if (glob.glob(f"{path_to_read}/*.zip")) != 0:
            file_c = glob.glob(f"{path_to_read}/*.zip")
            for file in file_c:
                filename = os.path.basename(file)
                href = file[file.find('static'):]
                csv_files.insert(0, {filename: href})
                print("me file: ", csv_files)
            context['csv_files'] = csv_files

    
    os.chdir(parent_dir)

    return context

def download_dataset(li_links, link, user):
    user = str(user) # for creating a folder in the partcular users name
    
    os.chdir(download_full_path) # by default this folder is already created and on the same level with the app
    try: # check is the folder exist already before creating to avoid file exist error
        os.mkdir(user)
        os.chdir(user)
    except FileExistsError:
        os.chdir(user)
    
    for li in li_links:
        full_link_to_download = f"{link}/{li}"
        urllib.request.urlretrieve(full_link_to_download, li)
    user_dir = os.getcwd()
    #print("Full Download Link: ", user_dir)
    #latest_files = read_directory(user_dir)
    os.chdir(parent_dir) #returns the directory back to the home directory
    # retrieve_dataset_uci(user, download_full_path)
    

def scrap_download_page(html, request, user, url_path_to_download, link ):
    
    li_links = []
    
    soup = BeautifulSoup(html, 'html.parser')
    ul = soup.find('ul')
    try:
        li = ul.find_all('li')[1:]
        # see structure of li below hence why we need to select fro 1 down ie 1:
        #<ul><li><a href="/ml/machine-learning-databases/"> Parent Directory</a></li>
        #<li><a href="3D_spatial_network.txt"> 3D_spatial_network.txt</a></li>
        #</ul>
        for i in li:
            clean_i = str(i).replace(" ", "")
            start_point = clean_i.find('">')+2
            end_point = clean_i.find('</')
            li_links.append(clean_i[start_point:end_point])
    except AttributeError:
        messages.error(request, "The link is empty, nothing to download. Please select another dataset")
    
    download_dataset(li_links, link, user)
    path_to_download = f"https://archive.ics.uci.edu/ml/machine-learning-databases/00528/dataset.csv"
    #webbrowser.open(path_to_download)
    

def uci_download_dataset(term, user, request):
    url_path_to_download = f"https://archive.ics.uci.edu/ml/datasets/{term}"
    url_to_scrap = get_dataset_download_url(url_path_to_download)    
    soup = BeautifulSoup(url_to_scrap, 'html.parser')
    table = soup.find('table', attrs={
        'width': '100%',
        'border': '0',
        'cellpadding': '2',
    })
    span = table.find('span', attrs={'class': 'normal'})
    a_tag = str(span.find_next('a'))
    start_point = a_tag.find('"')+1
    end_point = a_tag.find('/"')
    link_first_path = "https://archive.ics.uci.edu/ml"
    link_second = a_tag[start_point:end_point].replace("..", "")
    
    # you have to look at UCI dataset to fully understand this
    # link_second part has ../machine-learning-databases/00246/
    #link is the page that contains the dataset files
    link = link_first_path+link_second
    html = get_download_dataset_url(link)
    scrap_download_page(html, request, user, url_path_to_download, link)
    




    

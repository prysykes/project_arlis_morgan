import os
import pandas as pd
import csv
import glob
import boto3
import time
from google.cloud import language_v1
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from sklearn.metrics import f1_score, precision_score, accuracy_score, recall_score
import plotly.express as px


parent_dir = os.getcwd()
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'arlis-project-0bcfe8c25e89.json'

media = os.path.join(parent_dir, 'media')
csv_dir = os.path.join(media, 'nlp_csv')

key = "0f7d590cdc31405c948c75f91e6f2965"
endpoint = "https://arlis-project.cognitiveservices.azure.com/"



# parent_dir = os.getcwd()
# media = os.path.join(parent_dir, 'media')
# csv_dir = os.path.join(media, 'nlp_csv')
cred_pad = '/Users/prynet/Documents/aws_cred/emeka_accessKeys.csv'
df = pd.read_csv(cred_pad)
# print(df.columns)
# df.index[0] returns first row, second argument is the column name
access_key_id = df.loc[df.index[0], 'Access key ID']

secret_key_id = df.loc[df.index[0], 'Secret access key']


# if len(glob.glob(f"{csv_dir}/*.csv") )!= 0:
# csv_file = glob.glob(f"{csv_dir}/*.csv")[0]
# new_df = pd.read_csv(csv_file)[0:1500]



#the following arrays holds metrics for benchmarking

aws_Result = []
Amazon_Total = []

google_Result = []
Google_Total= []

Azure_Total = []
Azure_target = []


# definging variables for plot
New_Data_target = []

result_Amazon = []

Google_target = []





# def populate_api_context(context, all_accuracy, all_f1_score, all_precision, all_recall, platform_compute_times):
#     # provides the structure of data that is returned at the api response.
#     #accuracy object
#     context['Accuracies'].setdefault('amazon', all_accuracy[0]) 
#     context['Accuracies'].setdefault('azure', all_accuracy[1])
#     context['Accuracies'].setdefault('google', all_accuracy[2])

#     #f1 score object
#     context['F1Score'].setdefault('amazon', all_f1_score[0])
#     context['F1Score'].setdefault('azure', all_f1_score[1])
#     context['F1Score'].setdefault('google', all_f1_score[2])

#     #precision object
#     context['Precision'].setdefault('amazon', all_precision[0])
#     context['Precision'].setdefault('azure', all_precision[1])
#     context['Precision'].setdefault('google', all_precision[2])

#     #recall object
#     context['Recall'].setdefault('amazon', all_recall[0])
#     context['Recall'].setdefault('azure', all_recall[1])
#     context['Recall'].setdefault('google', all_recall[2])

#     #compute times object
#     context['ComputeTimes'].setdefault('amazon', platform_compute_times[0])
#     context['ComputeTimes'].setdefault('azure', platform_compute_times[1])
#     context['ComputeTimes'].setdefault('google', platform_compute_times[2])


# def nlp_api_call_processor(working_df):
#     print("processing api calls")
#     context = {'Accuracies': {},
#                'F1Score': {},
#                'Precision': {},
#                'Recall': {},
#                'ComputeTimes': {}}
#     New_Data_target = working_df['target']

#     result_Amazon = working_df['AWS']

#     Google_target = working_df['GCP']

#     Azure_target = working_df['AZURE']
#     #print("printing >>", New_Data_target, result_Amazon, Google_target, Azure_target)
#     amazon_f1_score = f1_score(New_Data_target, result_Amazon, average='macro')
#     amazon_accuracy = accuracy_score(New_Data_target, result_Amazon)
#     amazon_precision = precision_score(New_Data_target, result_Amazon, average='macro')
#     amazon_recall = recall_score(New_Data_target, result_Amazon, average='macro')
    

#     google_f1_score = f1_score(New_Data_target, Google_target, average='macro')
#     google_accuracy = accuracy_score(New_Data_target, Google_target)
#     google_precision = precision_score(New_Data_target, Google_target, average='macro')
#     google_recall = recall_score(New_Data_target, Google_target, average='macro')
    

#     azure_f1_score = f1_score(New_Data_target, Azure_target, average='macro')
#     azure_accuracy = accuracy_score(New_Data_target, Azure_target)
#     azure_precision = precision_score(New_Data_target, Azure_target, average='macro')
#     azure_recall = recall_score(New_Data_target, Azure_target, average='macro')
    

#     all_accuracy = [amazon_accuracy, azure_accuracy, google_accuracy]
#     all_f1_score = [amazon_f1_score, azure_f1_score, google_f1_score]
#     all_precision = [amazon_precision, azure_precision, google_precision]
#     all_recall = [amazon_recall, azure_recall, google_recall]

#     platform_compute_times = [sum(Amazon_Total), sum(Azure_Total), sum(Google_Total)]

#     populate_api_context(context, all_accuracy, all_f1_score, all_precision, all_recall, platform_compute_times)
#     print("platform processing time list", platform_compute_times)
    
#     return context
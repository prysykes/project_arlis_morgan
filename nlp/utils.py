import os
import shutil
import pandas as pd
import csv
import glob
import boto3
import time
import plotly.express as px
from google.cloud import language_v1
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from sklearn.metrics import f1_score, precision_score, accuracy_score, recall_score
# from .api_utils import nlp_api_call_processor


parent_dir = os.getcwd()
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'arlis-project-0bcfe8c25e89.json'

media = os.path.join(parent_dir, 'media')
csv_dir = os.path.join(media, 'nlp_csv')


# parent_dir = os.getcwd()
# media = os.path.join(parent_dir, 'media')
# csv_dir = os.path.join(media, 'nlp_csv')
cred_pad = '/Users/prynet/Documents/aws_cred/emeka_accessKeys.csv'
df = pd.read_csv(cred_pad)
# print(df.columns)
# df.index[0] returns first row, second argument is the column name
access_key_id = df.loc[df.index[0], 'Access key ID']

secret_key_id = df.loc[df.index[0], 'Secret access key']


key = "0f7d590cdc31405c948c75f91e6f2965"
endpoint = "https://arlis-project.cognitiveservices.azure.com/"



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








def read_uploaded_csv(csv_folder):
    csv_file = glob.glob(f"{csv_folder}/*.csv")[0]
    print(os.path.isfile(csv_file))
    #get only the csv files then use pagination to display requested page
    # df = pd.read_csv(csv_file).head(5).to_html()
    with open(csv_file, mode='r') as read_obj:
        csv_reader = csv.reader(read_obj)
        df = list(csv_reader)
    # print(df)

    return df

# Begin AWS sentiment analyis


comprehend = boto3.client('comprehend', region_name='us-east-1')

#AWS Statsj
"""aws_Result = []
Amazon_Total = []"""


def aws_get_sentiment(mytxt):
    Amazon_TimeStart = time.time()
    response = comprehend.detect_sentiment(Text=mytxt, LanguageCode='en')

    Amazon_TimeEnd = time.time()
    Amazon_Time = Amazon_TimeEnd - Amazon_TimeStart
    Amazon_Total.append(Amazon_Time)
    # print(response['Sentiment'])
    return response['Sentiment']


# Google GCP Stats
"""google_Result = []
Google_Total= []"""

def google_Analyze_Sentiment(mytext):
    
    client = language_v1.LanguageServiceClient()
    # text = u""" I am happy """

    document = language_v1.Document(
        content=mytext, type_=language_v1.Document.Type.PLAIN_TEXT
    )
    #intializing time for GCP
    Google_TimeStart = time.time()
    sentiment = client.analyze_sentiment(
        request={"document": document}
        ).document_sentiment


    Google_TimeEnd = time.time() #arecord of the stop time

    Google_Time = Google_TimeEnd - Google_TimeStart
    Google_Total.append(Google_Time)

    if sentiment.score == 0:
        google_Result.append('neutral')
    elif sentiment.score > 0:
        google_Result.append('positive')
    else:
        google_Result.append('negative')
    return google_Result


# Authenticate the client using your key and endpoint 
def authenticate_client(): 
    ta_credential = AzureKeyCredential(key)
    text_analytics_client = TextAnalyticsClient(endpoint=endpoint, credential=ta_credential)
    return text_analytics_client
client = authenticate_client()


def Azure_sentiment_analysis(client, documents):
    # Azure Start Time
    Azure_TimeStart = time.time()
    response = client.analyze_sentiment(documents=[documents])[0]
    # Azure End Time
    Azure_TimeEnd = time.time()
    Azure_Time = Azure_TimeEnd - Azure_TimeStart
    Azure_Total.append(Azure_Time)
    # Append the result to the list 
    Azure_target.append(response.sentiment)


def insert_into_original_df(new_df):
    """ This function add these columns to the orginal data frame"""
    # csv_file = glob.glob(f"{csv_dir}/*.csv")[0]
    # new_df = pd.read_csv(csv_file)[0:1500]
    new_df['AWS'] = new_df['AWS Upper'].apply(lambda x: x.lower())

    new_df['GCP'] = google_Result
    new_df['AZURE'] = Azure_target
    #drops the following columns ''AWS Upper', 'Not used', 'Azure not uswd'' and selects all collumnas without the mixed
    main_df= new_df.drop(['AWS Upper', 'Not used', 'Azure not uswd'], axis=1).loc[new_df['AWS'] != 'mixed'] 
    return main_df

def plot_benchmark_metrics(*metrics):
    """
        This function expects an number of lists 
        each represing computed metrics for each playform
        metrics[0] = all_accuracy = [amazon_accuracy, azure_accuracy, google_accuracy]
        metrics[1] = all_f1_score = [amazon_f1_score, azure_f1_score, google_f1_score]
        metrics[2] = all_precision = [amazon_precision, azure_precision, google_precision]
        metrics[3] = all_recall = [amazon_recall, azure_recall, google_recall]
        metrics[4] = platform_compute_times = [sum(Amazon_Total), sum(Google_Total), sum(Azure_Total)]
    """
    all_benchmark_data = [*metrics[0], *metrics[1], *metrics[2], *metrics[3]] #* is a spread operator in python
    platform_processing_times = [*metrics[4]]
    print(all_benchmark_data)
    data = pd.DataFrame({
        "Platform": ["AWS","Azure", "GCP", "AWS", "Azure", "GCP", "AWS", "Azure", "GCP","AWS", "Azure", "GCP"], 
        "Performance" : all_benchmark_data,   
        "Performance Metrics" : ["Accuracy","Accuracy","Accuracy", "F1_Score", "F1_Score", "F1_Score", "Precision", "Precision", "Precision", "Recall", "Recall", "Recall"],
    })

    data2 = pd.DataFrame({
    "Platforms" : ["AWS", "Azure", "GCP"],
    "Time(s)" : platform_processing_times,
    "Cloud Services" :["Amazon Time", "Azure Time", "Google Time"]
})
    fig = px.bar(data, x = "Performance Metrics", y = "Performance", color="Platform", barmode="group")
    fig1 = px.bar(data2, x = "Cloud Services", y = "Time(s)", color="Platforms", barmode="group")
    chart = fig.to_html() 
    chart2 = fig1.to_html() 
    context = {'chart': chart,
               'chart2': chart2}

    return context  


def select_df_columns(working_df):
    print("selecting columns for plot...")
    New_Data_target = working_df['target']

    result_Amazon = working_df['AWS']

    Google_target = working_df['GCP']

    Azure_target = working_df['AZURE']
    #print("printing >>", New_Data_target, result_Amazon, Google_target, Azure_target)
    amazon_f1_score = f1_score(New_Data_target, result_Amazon, average='macro')
    amazon_accuracy = accuracy_score(New_Data_target, result_Amazon)
    amazon_precision = precision_score(New_Data_target, result_Amazon, average='macro')
    amazon_recall = recall_score(New_Data_target, result_Amazon, average='macro')
    

    google_f1_score = f1_score(New_Data_target, Google_target, average='macro')
    google_accuracy = accuracy_score(New_Data_target, Google_target)
    google_precision = precision_score(New_Data_target, Google_target, average='macro')
    google_recall = recall_score(New_Data_target, Google_target, average='macro')
    

    azure_f1_score = f1_score(New_Data_target, Azure_target, average='macro')
    azure_accuracy = accuracy_score(New_Data_target, Azure_target)
    azure_precision = precision_score(New_Data_target, Azure_target, average='macro')
    azure_recall = recall_score(New_Data_target, Azure_target, average='macro')
    

    all_accuracy = [amazon_accuracy, azure_accuracy, google_accuracy]
    all_f1_score = [amazon_f1_score, azure_f1_score, google_f1_score]
    all_precision = [amazon_precision, azure_precision, google_precision]
    all_recall = [amazon_recall, azure_recall, google_recall]

    platform_compute_times = [sum(Amazon_Total), sum(Azure_Total), sum(Google_Total)]


    #print(f" Amazon Total: {sum(Amazon_Total)} \n Google_total: {sum(Google_Total)} \n Azure Total: {sum(Azure_Total)}")
    return plot_benchmark_metrics(all_accuracy, all_f1_score, all_precision, all_recall, platform_compute_times)

def populate_api_context(context, all_accuracy, all_f1_score, all_precision, all_recall, platform_compute_times):
    # provides the structure of data that is returned at the api response.
    #accuracy object
    context['Accuracies'].setdefault('amazon', all_accuracy[0]) 
    context['Accuracies'].setdefault('azure', all_accuracy[1])
    context['Accuracies'].setdefault('google', all_accuracy[2])

    #f1 score object
    context['F1Score'].setdefault('amazon', all_f1_score[0])
    context['F1Score'].setdefault('azure', all_f1_score[1])
    context['F1Score'].setdefault('google', all_f1_score[2])

    #precision object
    context['Precision'].setdefault('amazon', all_precision[0])
    context['Precision'].setdefault('azure', all_precision[1])
    context['Precision'].setdefault('google', all_precision[2])

    #recall object
    context['Recall'].setdefault('amazon', all_recall[0])
    context['Recall'].setdefault('azure', all_recall[1])
    context['Recall'].setdefault('google', all_recall[2])

    #compute times object
    context['ComputeTimes'].setdefault('amazon', platform_compute_times[0])
    context['ComputeTimes'].setdefault('azure', platform_compute_times[1])
    context['ComputeTimes'].setdefault('google', platform_compute_times[2])


def nlp_api_call_processor(working_df):
    print("processing api calls")
    context = {'Accuracies': {},
               'F1Score': {},
               'Precision': {},
               'Recall': {},
               'ComputeTimes': {}}
    New_Data_target = working_df['target']

    result_Amazon = working_df['AWS']

    Google_target = working_df['GCP']

    Azure_target = working_df['AZURE']
    #print("printing >>", New_Data_target, result_Amazon, Google_target, Azure_target)
    amazon_f1_score = f1_score(New_Data_target, result_Amazon, average='macro')
    amazon_accuracy = accuracy_score(New_Data_target, result_Amazon)
    amazon_precision = precision_score(New_Data_target, result_Amazon, average='macro')
    amazon_recall = recall_score(New_Data_target, result_Amazon, average='macro')
    

    google_f1_score = f1_score(New_Data_target, Google_target, average='macro')
    google_accuracy = accuracy_score(New_Data_target, Google_target)
    google_precision = precision_score(New_Data_target, Google_target, average='macro')
    google_recall = recall_score(New_Data_target, Google_target, average='macro')
    

    azure_f1_score = f1_score(New_Data_target, Azure_target, average='macro')
    azure_accuracy = accuracy_score(New_Data_target, Azure_target)
    azure_precision = precision_score(New_Data_target, Azure_target, average='macro')
    azure_recall = recall_score(New_Data_target, Azure_target, average='macro')
    

    all_accuracy = [amazon_accuracy, azure_accuracy, google_accuracy]
    all_f1_score = [amazon_f1_score, azure_f1_score, google_f1_score]
    all_precision = [amazon_precision, azure_precision, google_precision]
    all_recall = [amazon_recall, azure_recall, google_recall]

    platform_compute_times = [sum(Amazon_Total), sum(Azure_Total), sum(Google_Total)]

    populate_api_context(context, all_accuracy, all_f1_score, all_precision, all_recall, platform_compute_times)
    print("platform processing time list", platform_compute_times)
    
    return context

def run_jobs(caller=None):
    csv_file = glob.glob(f"{csv_dir}/*.csv")[0]
    df.drop(df.index, inplace=True) # empties the data frame to overcome the list index error
    new_df = pd.read_csv(csv_file)[0:50]
    
    new_df['AWS Upper'] = new_df['text'].apply(lambda x: aws_get_sentiment(str(x)))
    new_df['Not used'] = new_df['text'].apply(lambda x: google_Analyze_Sentiment(str(x)))
    new_df['Azure not uswd'] = new_df['text'].apply(lambda x: Azure_sentiment_analysis(client, str(x)))

    if caller == 'api':
        #checks if the payload was sent from the API or the workbench directly
        working_df = insert_into_original_df(new_df)
        return nlp_api_call_processor(working_df)
    else:
        working_df = insert_into_original_df(new_df)
        return select_df_columns(working_df)


        
    #main_df= new_df.drop(['AWS Upper', 'Not used', 'Azure not uswd'], axis=1)
    #print(working_df.head(5))

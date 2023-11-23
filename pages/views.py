import json
import os
import pandas as pd
from django.http import JsonResponse
import boto3
from django.shortcuts import redirect, render, HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .elastic_search_utils import search_opensearch_handler, custom_elasticsearch_query, get_img_date, session
from .utils import points_within_radius, delete_dir_contents

from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth


cred_pad = '/Users/prynet/Documents/aws_cred/emeka_accessKeys.csv'
df = pd.read_csv(cred_pad)
access_key_id = df.loc[df.index[0], 'Access key ID'] #df.index[0] returns first row, second argument is the column name 
secret_key_id = df.loc[df.index[0], 'Secret access key']
# region_name = 'us-east-1'
host = 'https://search-arlis-elastic-search-sd2nol57xt4edikcbmyfr65xie.us-east-1.es.amazonaws.com' # cluster endpoint, for example: my-test-domain.us-east-1.es.amazonaws.com
port = 443
region = 'us-east-1'
parent_dir = os.getcwd()
temp_imgs_s3 = os.path.join(parent_dir, 'media', 'temp_imgs_s3')


@login_required(login_url='user_login')
def index(request):
    context = {}
    return render(request, 'index.html', context)


def search_dataset(request, search_string):
    context = {}
    return render()


def api_endpoint(request):
    pass

@login_required(login_url='user_login')
def elastic_search(request):
    
    delete_dir_contents(temp_imgs_s3)

    """
        params:
        object': ['televison'], 
        'longitude': ['45.98'], 
        'latitude': ['6655.998'], 
        'start_date': ['2023-08-01'], 
        'end_date': ['2023-08-17'], 
        'detections': ['6'], # 
        'object_area': ['88']}>

    """
    context = {}
    # print("requestty", request.data)
    credentials = boto3.Session().get_credentials()
    auth = AWSV4SignerAuth(credentials, region)
    client = OpenSearch(
        hosts = [f'{host}:{port}'],
        http_auth = auth,
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection
    )

    bucket_name = 'img-processing-bucket'
    s3 = session.client('s3')

    data = request.POST
    data = dict(data)
    # print(data)
    object_class = data['object'][0]
    # print(f"object cl$$ {object_class}")
    detections = None
    matching_img_idx = []
    if ('latitude' and 'longitude' and 'radius') in data:
        
        if ('object_area' and 'detections' and 'start_date' and 'end_date') not in data:
            # print('yes')
            search_query = {}
            search_query['latitude'] = data['latitude'][0]
            search_query['longitude'] = data['longitude'][0]
            search_query['radius'] = data['radius'][0]
            search_query['object'] = data['object'][0]

            # returns longitude and latide values close to given radius
            nearby_long_lat = points_within_radius(float(search_query['latitude']), \
                                                    float(search_query['latitude']), float(search_query['radius']))
            # print(nearby_long_lat)

            field_to_search = "latitude_field"
            imgs_wt_bb  = custom_elasticsearch_query(request, client, search_query, object_class, field_to_search)
    
            img_id_metrics = {}
            for img_id in imgs_wt_bb:
                #used to populate the summary of detections and insights per img
                s3_object = s3.get_object(Bucket=bucket_name, Key=f'img-metrics/{img_id}.json')
                # s3_object = s3.Object(bucket_name, f'img-metrics/{img_id}.json')
                # img_metrics = s3_object.get()['Body'].read().decode('utf-8')
                # img_metrics = s3_object.get()['Body'].read().decode('utf-8')
                img_metrics = s3_object['Body'].read().decode('utf-8')
                img_metrics = str(img_metrics)
                img_metrics = img_metrics.replace('\r\n', '')
                img_metrics = dict(json.loads(img_metrics))
                # print("type type", type(img_metrics))
                img_id_metrics.setdefault(img_id, img_metrics)
                
            # print("presigned_url presigned_url", presigned_url)
            # print("img_id_metrics", img_id_metrics)

            context = {"img_id_metrics": img_id_metrics,
                    }
            # print(search_query)
    elif ('latitude' and 'longitude' \
           and 'radius' and 'object_area' \
              and 'start_date' and 'end_date') not in data:
        if ('detections' in data):
            search_query = data['detections'][0]
            # print(f"detections {search_query}")
            field_to_search = "dectections_field"

    elif ('latitude' and 'longitude' \
           and 'radius' and 'object_area' \
              and 'detections' ) not in data:
        if ('start_date' and 'end_date') in data:
            # start_date = 2
            # end_date = 3
            start_date = data['start_date'][0]
            end_date = data['end_date'][0]
            # print(start_date, end_date)
            date_range = (start_date, end_date)
            # print('date range', date_range)
            search_query = date_range 
            # print(f"detections {search_query}")
            field_to_search = "DateTime"
            response = get_img_date(client, field_to_search, date_range, object_class)
            # print('response', response)
            return 'yes'
            

    
    # for key, value in data.items():
    #     if key == "object":
    #         object_class = value[0]
    #     if key == "detections":
    #         detections = value[0]
    # # print(object_class, detections)
    # search_query = detections
    # field_to_search = "dectections_field"


    
    # for search_field, value in data.items():
    #     print("value", value, len(value), search_field)
    # print("dataaaa", data)
    

    
    # s3.meta.client.download_file(bucket_name, object_key, f'{temp_imgs_s3}/{object_key}.jpg')
    
    
    
    context = json.dumps(context, indent=2)
    # return render(request, 'index.html', context)
    
    return HttpResponse(context)

def search_opensearch(request, search_string):
    user = request.user 
    search_opensearch_handler(user, search_string)
    print(user, search_string)
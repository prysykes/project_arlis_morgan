import os
import boto3
import pandas as pd

from .utils import euclidean_dist
from pages.utils import delete_dir_contents


from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth

from .utils import draw_bb_on_s3_downlds, retrieve_bb, read_img_wt_bb


cred_pad = '/Users/prynet/Documents/aws_cred/emeka_accessKeys.csv'
df = pd.read_csv(cred_pad)
access_key_id = df.loc[df.index[0], 'Access key ID'] #df.index[0] returns first row, second argument is the column name 
secret_key_id = df.loc[df.index[0], 'Secret access key']
# region_name = 'us-east-1'
host = 'https://search-arlis-elastic-search-sd2nol57xt4edikcbmyfr65xie.us-east-1.es.amazonaws.com' # cluster endpoint, for example: my-test-domain.us-east-1.es.amazonaws.com
port = 443
region = 'us-east-1'


parent_dir = os.getcwd()
media = os.path.join(parent_dir, 'media')
test_images_dir = os.path.join(media, 'test_images')
test_csv_dir = os.path.join(media, 'test_csv')
yolo_result = os.path.join(media, 'result_yolo')
aws_result = os.path.join(media, 'result_aws')
csv_files = os.path.join(media, 'csv_for_scores')

temp_imgs_s3 = os.path.join(media, 'temp_imgs_s3')


session = boto3.Session(aws_access_key_id=access_key_id,
                        aws_secret_access_key=secret_key_id,
                        region_name=region)

def insert_into_aws_opensearch(username, doc, index):
    # doc_index= str(username)+"_"+index

    doc_index= 'odni'
    

    credentials = boto3.Session().get_credentials()
    auth = AWSV4SignerAuth(credentials, region)

    client = OpenSearch(
    hosts = [f'{host}:{port}'],
    http_auth = auth,
    use_ssl = True,
    verify_certs = True,
    connection_class = RequestsHttpConnection
    )

    response = client.index(
        index=doc_index,
        body=doc
    )
    return response['_id']
    print("insert into opensearch payload", response)

def return_indices_associated_with_user(current_user):
    credentials = boto3.Session().get_credentials()
    auth = AWSV4SignerAuth(credentials, region)
    client = OpenSearch(
        hosts = [f'{host}:{port}'],
        http_auth = auth,
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection
    )

    response = client.indices.get('*')
    domain_names = list(response.keys())
    matching_indices = [domain_name for domain_name in domain_names if current_user in domain_name]
    # print(f'matching_indices {matching_indices} \n user {current_user}')
    return matching_indices


def search_opensearch_handler(user, search_string):
    # print(type(search_string['body']['gps']))
    current_user = str(user)
    
    credentials = boto3.Session().get_credentials()
    auth = AWSV4SignerAuth(credentials, region)
    client = OpenSearch(
        hosts = [f'{host}:{port}'],
        http_auth = auth,
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection
    )
    indices = return_indices_associated_with_user(current_user)
    first_key = search_string['body'].keys()
    # print(first_key[0])
    query = first_key
    response = client.search(
        index = indices,
        # index = "emmy-new_index",
        body={
            'query' : {
                'query_string' : {
                    'query': query
                }
            }
        }
    )
    
    # print(response)

def build_path(fields, object_class=None):
    """
        Common Paths found in the document includes
        image_name.metadata.img_dimensions.width
        image_name.metadata.img_dimensions.height
        image_name.metadata.DateTime
        image_name.metadata.GPSInfo


        image_name.img_insights.num_objects
        image_name.img_insights.class_conf_bb_seg.{class_detection}.confidence
        image_name.img_insights.class_conf_bb_seg.{class_detection}.area
        image_name.img_insights.class_conf_bb_seg.{class_detection}.bb
        image_name.img_insights.class_conf_bb_seg.{class_detection}.seg
        
    """
    common_field_names = list(fields.keys())

    image_name = fields['image_name']
    metadata = common_field_names[1]
    img_insights = common_field_names[2]
    GPSInfo = common_field_names[3]
    DateTime = common_field_names[4]
    img_dimensions = common_field_names[5]
    width = common_field_names[6]
    height = common_field_names[7]
    num_objects = common_field_names[8]
    class_conf_bb_seg = common_field_names[9]
    detection_classes = common_field_names[10]
    confidence = common_field_names[11]
    area = common_field_names[12]
    bb = common_field_names[13]
    seg = common_field_names[14]
    # print(f"build path {object_class}")

    
    num_objects_field = f"{image_name}.{img_insights}.{num_objects}"
    object_area_field = f"{image_name}.{img_insights}.{class_conf_bb_seg}.{object_class}.{area}"
    bb_field = f"{image_name}.{img_insights}.{class_conf_bb_seg}.{object_class}.{bb}"
    # print(f"bb_field {bb_field}")
    
    DateTime_field = f"{image_name}.{metadata}.{DateTime}"
    latitude_field = f"{image_name}.{metadata}.{GPSInfo}.latitude"
    longitude_field = f"{image_name}.{metadata}.{GPSInfo}.longitude"
    

    fields_to_search = {'dectections_field': num_objects_field,
                        'object_area_field': object_area_field,
                        'bb_field': bb_field,
                        'DateTime_field': DateTime_field,
                        'latitude_field': latitude_field,
                        'longitude_field': longitude_field}
    
    # print("abiii", fields_to_search)
    return fields_to_search


def prepare_custom_fields(client, documents, index_name):
    """
        prepares a custome field for an image, using image names
    """
    fields = {}

    #obtain a document id
    try:
        document_id = documents['hits']['hits'][0]['_id']
    except Exception as e:
        print(e)
    
    #retrieve a document 
    first_doc = client.get(index_name, id=document_id)

    image_name = list(first_doc['_source'].keys())[0]
    fields['image_name'] = image_name
    # print("docc ", document_name)
    # print("image nameee ", image_name)

    #all docs have the same field format. u
    # using first doc to build format for all docs
    first_doc_fields = first_doc['_source'][image_name]

    metadata = first_doc_fields['metadata']
    fields['metadata'] = metadata

    img_insights = first_doc_fields['img_insights']
    fields['img_insights'] = img_insights

    GPSInfo = metadata['GPSInfo']
    fields['GPSInfo'] = GPSInfo

    DateTime = metadata['DateTime']
    fields['DateTime'] = DateTime
    
    #extract original image width and height from image diementions key
    img_dimensions = metadata['img_dimensions']
    fields['img_dimensions'] = img_dimensions

    width = img_dimensions['width']
    fields['width'] = width

    height = img_dimensions['height']
    fields['height'] = height

    
    num_objects = img_insights['num_objects']
    fields['num_objects'] = num_objects

    # build path for image insights for all detections
    class_conf_bb_seg = img_insights['class_conf_bb_seg']
    fields['class_conf_bb_seg'] = class_conf_bb_seg

    #retieve classes of objects detected
    detection_classes = list(class_conf_bb_seg.keys())
    fields['detection_classes'] = detection_classes #list of detections in the image
    first_dectection_class = list(class_conf_bb_seg.keys())[0]

    common_fields_in_detections = class_conf_bb_seg[first_dectection_class]

    confidence = common_fields_in_detections[0]['confidence']
    fields['confidence'] = confidence

    area = common_fields_in_detections[0]['area']
    fields['area'] = area

    bb = common_fields_in_detections[0]['bb']
    fields['bb'] = bb

    seg = common_fields_in_detections[0]['seg']
    fields['seg'] = seg

    # print("fieldsss", fields)
    return fields

def get_img_or_presignedurl(name_bb_obj_name, response=None, object_id=None, image_name=None):
    """ Download image from s3bucket if object key is provided or generate a presigned url through
        parent function response argument
    """
    img_dir = temp_imgs_s3
    
    img_or_presignedurl = None
    if object_id != None:
        bucket_name = 'img-processing-bucket'
        # print("object key", object_key)
        s3 = session.resource('s3')
        s3.meta.client.download_file(bucket_name, object_id, f'{temp_imgs_s3}/{object_id}.jpg')
        img_or_presignedurl = s3.meta.client.generate_presigned_url('get_object', 
                                                Params={'Bucket': bucket_name, 'Key': object_id},
                                                    ExpiresIn=3600)
        img_or_presignedurl = img_or_presignedurl
    else:
        if not isinstance(response, Exception):
            object_id = response['hits']['hits'][0]['_id']
            bucket_name = 'img-processing-bucket'

            s3 = session.resource('s3')

            img_or_presignedurl = s3.meta.client.generate_presigned_url('get_object', 
                                                    Params={'Bucket': bucket_name, 'Key': object_id},
                                                        ExpiresIn=3600)
            
            
            img_or_presignedurl = img_or_presignedurl
    downloaded_imgs = os.listdir(img_dir) #contains a list of images, that met the search criteria downloaded from s3 bucket
   
    draw_bb_on_s3_downlds(image_name, object_id, downloaded_imgs, name_bb_obj_name, img_dir)
    
    return img_or_presignedurl

def get_images_lat_long_fields_bb(client, image_names, fields_to_search, object_class, index_name='odni'):
    img_id_lat_long_bb = {}

    bb_field = fields_to_search[ 'bb_field']
    
    for idx, img in enumerate(image_names):
        cur_img_bbs = retrieve_bb(img, object_class, fields_to_search, client, index_name)
        print(f"len(cur_img_bbs) {len(cur_img_bbs)}")
        
        latitude_field = fields_to_search['latitude_field']
        first_dot_lat = latitude_field.find('.')
        cur_image_name_lat  = img + latitude_field[first_dot_lat:]

        longitude_field = fields_to_search['longitude_field']       
        
        first_dot_long = longitude_field.find('.')
        cur_image_name_long = img + longitude_field[first_dot_long:]
        # print(f'Image: {img} \n cur latitude field: {cur_image_name_lat} \n cur longitude_field: {cur_image_name_long}')


        query_for_lat_long_val = {
            "query": {
                "match_all": {}
            },
            "_source": [cur_image_name_lat, cur_image_name_long]
            
        }

        lat_long_fields = client.search(index=index_name, body=query_for_lat_long_val)
        # print("l===at_long_fields ==", lat_long_fields)
        lat_long_fields = lat_long_fields['hits']['hits'][idx]
        
        current_img_id = lat_long_fields['_id']
        cur_lat = lat_long_fields['_source'][img]['metadata']['GPSInfo']['latitude']
        cur_long = lat_long_fields['_source'][img]['metadata']['GPSInfo']['longitude']
        cur_lt_long = {'latitude': cur_lat,
                       'longitude': cur_long,
                       'cur_img_name': img,
                       }
        
        # for hit in lat_long_fields['hits']['hits']:
        #     if len(hit['_source'].keys()) != 0:
        #         bb = hit['_source'][f'{img}']['img_insights']['class_conf_bb_seg']['person_1'][0]['bb']
        #         print("yes", bb)
        
        img_id_lat_long_bb.setdefault(current_img_id,{})
        img_id_lat_long_bb[current_img_id].setdefault('bb', cur_img_bbs)
        img_id_lat_long_bb[current_img_id].setdefault('lat_long', cur_lt_long)
        img_id_lat_long_bb[current_img_id].setdefault('hit_count', len(cur_img_bbs))
        # img_id_lat_long['response'] = lat_long_fields
   
    return img_id_lat_long_bb

def get_img_date(client, field_to_search, date_range, object_class=None, index_name='odni'):
    image_ids_date_time = {}
    image_names = []
    

    query_for_index = {
        "query": {
            "match_all": {}
        }
    }

    # returns all documents in the provided index
    documents = client.search(index=index_name, body=query_for_index)
   
    fields = prepare_custom_fields(client, documents, index_name)    
    fields_to_search = build_path(fields, object_class)

    # print(f"fields {fields}")
    # print(f"fields_to_search {fields_to_search}")
   
    for doc in documents['hits']['hits']:
        image_name = list(doc['_source'].keys())[0]
        image_names.append(image_name)
    # print(image_names, "image names")

    if object_class:
        for idx, img_name in enumerate(image_names):
            #returns the date time field of an image
            #datetime field of other images are now built from this
            img_date_field = fields_to_search['DateTime_field']
            field_img_name = img_date_field.split('.')[0]
            cur_img_date_time_field = img_date_field.replace(field_img_name, img_name)
            # print("cur_img_date_time_field", cur_img_date_time_field)
            # print("img_date_field", img_date_field)

            query_for_date_field = {
                "query": {
                    "match_all": {}
                },
                "_source": [cur_img_date_time_field]
            }
            date_time_value = client.search(index=index_name, body=query_for_date_field)
            for hit in date_time_value['hits']['hits']:
                if len(hit['_source'].keys()) != 0:
                    print("cur_hit", hit)
                    # cur_img_date_time = 
            print(date_time_value['hits']['hits'])

            return date_time_value
    #run the search over all the documents
    #irrespective of the class

def custom_elasticsearch_query(request, client, search_query, object_class, field_to_search, index_name='odni'):
    # print(f"custome search {search_query}")
    
    
    query_for_index = {
        "query": {
            "match_all": {}
        }
    }

    # print(f'object class {object_class}')
    # returns all documents in the provided index
    documents = client.search(index=index_name, body=query_for_index)
   
    fields = prepare_custom_fields(client, documents, index_name)
    fields_to_search = build_path(fields, object_class)
    # print(f"fields_to_search *** {fields_to_search}")
    field = fields_to_search[field_to_search]
   
    image_names = []
    
    presigned_url = []
    # query_for_bb_val = {
    #         "query": {
    #             "match_all": {}
    #         },
    #         "_source": [new_bb_field]
            
    #     }

    for doc in documents['hits']['hits']:
        image_name = list(doc['_source'].keys())[0]
        image_names.append(image_name)
    # print(image_names, "image names")

    
    if isinstance(search_query, dict) and 'radius' in search_query.keys():
       
        img_id_lat_long_bb_hitcount = get_images_lat_long_fields_bb(client, image_names, fields_to_search, object_class, index_name='odni')
        # print('img_id_lat_long_bb', img_id_lat_long_bb)
        close_imgs_id = euclidean_dist(request, search_query, img_id_lat_long_bb_hitcount)
    
        # deletes images with bounding box in the local directory
        delete_dir_contents(temp_imgs_s3)
        if len(close_imgs_id.keys()) != 0:
            
            for img_id, name_bb_obj_name in close_imgs_id.items():
                image_name = name_bb_obj_name['img_name']
                cur_presigned_url = get_img_or_presignedurl(name_bb_obj_name, response=None, object_id=img_id, image_name=image_name)
                
                presigned_url.append(cur_presigned_url)
    
    
    

    imgs_wt_bb = read_img_wt_bb(temp_imgs_s3)
    return imgs_wt_bb 
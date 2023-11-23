import os
import boto3
import pandas as pd
from opensearchpy import Q
import json


from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth


cred_pad = '/Users/prynet/Documents/aws_cred/emeka_accessKeys.csv'
df = pd.read_csv(cred_pad)
access_key_id = df.loc[df.index[0], 'Access key ID'] #df.index[0] returns first row, second argument is the column name 
secret_key_id = df.loc[df.index[0], 'Secret access key']
# region_name = 'us-east-1'
host = 'https://search-arlis-elastic-search-sd2nol57xt4edikcbmyfr65xie.us-east-1.es.amazonaws.com' # cluster endpoint, for example: my-test-domain.us-east-1.es.amazonaws.com
port = 443
region = 'us-east-1'


session = boto3.Session(aws_access_key_id=access_key_id,
                        aws_secret_access_key=secret_key_id,
                        region_name=region)


"""
response = client.indices.delete(
    index = 'python-test-index'
)

"""



def delete_all_documents(index_name, client):
    try:
        response = client.indices.delete(
            index = index_name
        )
        print(f"successfully deleted {response['deleted']} documents from the index")
    except Exception as e:
        print(f"error deleting documents: {e}")

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

    
    num_objects_field = f"{image_name}.{img_insights}.{num_objects}"
    object_area_field = f"{image_name}.{img_insights}.{class_conf_bb_seg}.{object_class}.{area}"
    bb_field = f"{image_name}.{img_insights}.{class_conf_bb_seg}.{object_class}.{bb}"
    DateTime_field = f"{image_name}.{metadata}.{DateTime}"
    latitude_field = f"{image_name}.{metadata}.{GPSInfo}.latitude"
    longitude_field = f"{image_name}.{metadata}.{GPSInfo}.longitude"
    

    fields_to_search = {'num_objects_field': num_objects_field,
                        'object_area_field': object_area_field,
                        'bb_field': bb_field,
                        'DateTime_field': DateTime_field,
                        'latitude_field': latitude_field,
                        'longitude_field': longitude_field}
    
    # print(fields_to_search)
    return fields_to_search




def prepare_custom_fields(client, documents, index_name):
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

    first_doc_fields = first_doc['_source'][image_name]

    metadata = first_doc_fields['metadata']
    fields['metadata'] = metadata

    img_insights = first_doc_fields['img_insights']
    fields['img_insights'] = img_insights

    GPSInfo = metadata['GPSInfo']
    fields['GPSInfo'] = GPSInfo

    DateTime = metadata['DateTime']
    fields['DateTime'] =DateTime
    
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


def custom_elasticsearch_query(search_query, index_name):
    # data = request.POST.get('start_date')
    # print("daday", data)
    # print("dqy", query)


    credentials = boto3.Session().get_credentials()
    auth = AWSV4SignerAuth(credentials, region)
    client = OpenSearch(
        hosts = [f'{host}:{port}'],
        http_auth = auth,
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection
    )
    index_name = "odni"
    delete_all_documents(index_name, client)

    query_for_index = {
        "query": {
            "match_all": {}
        }
    }

    documents = client.search(index=index_name, body=query_for_index)

    #retrieve documents source before query
    query_for_index = {
        "query": {
            "match_all": {}
        }
    }

    documents = client.search(index=index_name, body=query_for_index)
    
    
    
    fields = prepare_custom_fields(client, documents, index_name)
    fields_to_search = build_path(fields)
    print('laty: ', fields_to_search['longitude_field'])
    
    


    # metadata keys:  dict_keys(['GPSInfo', 'DateTime', 'img_dimensions'])
    # image insight keys:  dict_keys(['num_objects', 'class_conf_bb_seg'])

    # print("GPSInfo: ", GPSInfo)
    # print("DateTime: ", DateTime)
    # print("img_dimensions", img_dimensions)
    # print("um_objects", num_objects) 
    # print("class_conf_bb_seg", class_conf_bb_seg.keys())

    #print list of all fiels in the document

    # print("fields; ", first_doc_fields)

    query_for_lat_long_val = {
        "query": {
            "match_all": {}
        },
        
    }

    query_for_lat_long_val = {
        "query": {
            "match_all": {}
        },
        "_source": ['IMG_1943.img_insights.class_conf_bb_seg.person_1.bb']
        
    }
    lat_long_fields = client.search(index=index_name, body=query_for_lat_long_val)
    print("lat long", lat_long_fields)
    for hit in lat_long_fields['hits']['hits']:
        if len(hit['_source'].keys()) != 0:
            bb = hit['_source']['IMG_1943']['img_insights']['class_conf_bb_seg']['person_1'][0]['bb']
            print("yes", bb)
        
    # print("len hits hist", len(lat_long_fields['hits']['hits']['_source'].keys()))
    # for doc in documents['hits']['hits']:
    #     document_source = list(doc['_source'].keys())[0]
    #     print("document source", document_source)

    #     query_3 = {
    #         'query' : {
    #             "multi_match" : {
    #                 "query": search_query,
    #                 'fields': ["*"]
    #             }
                
    #         }
    #     }
    #     response = client.search(
    #     index = 'odni',
    #     # index = "emmy-new_index",
    #     body = query_3
    #     )

    
    #     # print("document_source:  ", document_source)

    
    #     try:
    #         response['hits']['hits'][0]
    #         return response
    #     except IndexError as e:
    #         if "index out of range" in str(e):
    #             print("index out of range")
    #             return e
            
    # query = {
    #         'query' : {
    #             "query_string" : {
    #                 "query": search_query
    #             }
                
    #         }
    #     }
    # query_1 = {
    #         'match' : [
    #              {
    #                 "img_insights.class_conf_bbs.Female.bb": search_query
    #             }
    #         ]
    #     }
    # query_2 = {
    #         "query": {
    #             "nested": {
    #             "path": "img_insights.class_conf_bbs.Female.bb",
    #             "query": {
    #                 'match' : {
    #                     "query_string" : {
    #                         "img_insights.class_conf_bbs.Female.bb": search_query
    #             }
    #         }
    #             },
    #             "score_mode": "avg"
    #             }
    #         }
    #         }
    # query_3 = {
    #     'query' : {
    #         "multi_match" : {
    #             "query": search_query,
    #             'fields': ["IMG_1943.img_insights.class_conf_bb_seg.person.area"]
    #         }
            
    #     }
    # }
    # response = client.search(
    #     index = 'odni',
    #     # index = "emmy-new_index",
    #     body = query_3
    # )

    # document_names = response['hits']['hits'][0]['_source'].keys()
    # document_ids = response['hits']['hits'][0]['_id']

    document_names =  lat_long_fields['hits']['hits'][1]['_source'].keys()
    ducument_name = list(document_names)[0]
    document_lat = lat_long_fields['hits']['hits'][1]['_source'][ducument_name]['metadata']['GPSInfo']['latitude']
    document_long = lat_long_fields['hits']['hits'][1]['_source'][ducument_name]['metadata']['GPSInfo']['longitude']
   
    document_names = type(list(document_names)[0])
    document_ids = lat_long_fields['hits']['hits'][1]['_id']
    # print("all hits", lat_long_fields['hits']['hits'][0])

    # print("document names", document_names)
    print('document_lat_long', document_lat, document_long)
    print("document ids", document_ids)

    # # response = client.indices.get_mapping('odni')
    # mappings_keys = response['odni']['mappings'].keys()
    # doc_type = list(mappings_keys)[0]

    # schema = response['odni']['mappings'][doc_type]
    # print(len(response['hits']['hits']))
    # return response
fields = ["IMG_1981.img_insights.num_objects", ]
query = "15"
the_response = custom_elasticsearch_query(query, 'odni')
# print(type(the_response))

if not isinstance(the_response, Exception):
    object_key = the_response['hits']['hits'][0]['_id']
    bucket_name = 'img-processing-bucket'

    s3 = session.resource('s3')

    presigned_url = s3.meta.client.generate_presigned_url('get_object', 
                                            Params={'Bucket': bucket_name, 'Key': object_key},
                                                ExpiresIn=3600)
    
    print(presigned_url)


try:
    object_key = the_response['hits']['hits'][0]['_id']
    # return response
except IndexError as e:
    print(e)
# print("==", the_response['hits']['hits'][0]['_source'].keys())
# print("doc ID: ", the_response['hits']['hits'][0]['_id'])

bucket_name = 'img-processing-bucket'
# object_key = the_response['hits']['hits'][0]['_id']

s3 = session.resource('s3')

presigned_url = s3.meta.client.generate_presigned_url('get_object', 
                                          Params={'Bucket': bucket_name, 'Key': object_key},
                                               ExpiresIn=3600)
print(presigned_url)



# response = s3.Bucket(bucket_name).upload_file(file_path, doc_id)


# mapping_keys, doc_type, schema = custom_elasticsearch_query(query, 'odni')
# # print(f"mapping_keys: {mapping_keys} \t doc_type: {doc_type}")
# print("==", list(schema.keys()))
import os
import pandas as pd
from PIL import Image
from PIL.ExifTags import TAGS
import json
import cv2
import requests
import boto3
import math
import json

from pages.utils_segmentation import handle_meta_data_api_obj_det

# from vision.views import run_detection

cred_pad = '/Users/prynet/Documents/aws_cred/emeka_accessKeys.csv'
df = pd.read_csv(cred_pad)
access_key_id = df.loc[df.index[0], 'Access key ID'] #df.index[0] returns first row, second argument is the column name 
secret_key_id = df.loc[df.index[0], 'Secret access key']
# region_name = 'us-east-1'
# host = 'https://search-arlis-elastic-search-sd2nol57xt4edikcbmyfr65xie.us-east-1.es.amazonaws.com' # cluster endpoint, for example: my-test-domain.us-east-1.es.amazonaws.com
# port = 443
region = 'us-east-1'


session = boto3.Session(aws_access_key_id=access_key_id,
                        aws_secret_access_key=secret_key_id,
                        region_name=region)


def generate_api_response(csv_for_scores_dir):
    object_detection_api_rsp = {}
    csv_files = os.listdir(csv_for_scores_dir)
    for file in csv_files:
        file_full_path = os.path.join(csv_for_scores_dir, file)
        #file is eg yolo_boxes.cvs, aws_boxes.csv
        platform_name = file.split('_')[0]
        with open(file_full_path, 'r') as csv_file:
            print("into: ", file)
            df_reader = pd.read_csv(csv_file)
            for index, row in df_reader.iterrows():
                
                image_name = row[0]
                count = (df_reader['imagefile'] == image_name).sum()
                object_detection_api_rsp.setdefault(image_name,{})
                object_detection_api_rsp[image_name].setdefault('platforms', {})
                object_detection_api_rsp[image_name]['platforms'].setdefault(platform_name, {})
                object_detection_api_rsp[image_name]['platforms'][platform_name].setdefault('detections', count)
                object_detection_api_rsp[image_name]['platforms'][platform_name].setdefault('labels', {})
                object_detection_api_rsp[image_name]['platforms'][platform_name]['labels'].setdefault('persons', [])
                BB = [*row[2:]]
                object_detection_api_rsp[image_name]['platforms'][platform_name]['labels']['persons'].append(BB)
            # for line in csv_reader:
            #     print(line)
                # if len(line) == 0:
                #     continue
                # else:
                    
                #     image_name = line[0]
                #     image_api_response.setdefault(image_name,{})
                #     image_api_response[image_name].setdefault('platforms', {})
                #     image_api_response[image_name]['platforms'].setdefault(file, {})
                #     image_api_response[image_name]['platforms'][file].setdefault('detections',)
    return object_detection_api_rsp

def convert_to_dec_degrees(time_tupple, hemisphere):
    degrees = time_tupple[0]
    minutes = time_tupple[1]
    seconds = time_tupple[2]
    hemisphere = hemisphere
    
    if hemisphere == 'N' or hemisphere == 'E':
        return degrees + (minutes/60) + (seconds/3600)
    else:
        return degrees - (minutes/60) - (seconds/3600)

def points_within_radius(start_lon, start_lat, radius_mi):
    points = []
    # earth radius in in miles
    earth_radius_mi = 3958.8

    # Convert latitude and longitude from degrees to radians
    start_lon = math.radians(start_lon)
    start_lat = math.radians(start_lat)

    for bearing in range(0, 360):
        bearing_rad = math.radians(bearing)

        new_lat = math.asin(
            math.sin(start_lat) * math.cos(radius_mi / earth_radius_mi) +
            math.cos(start_lat) * math.sin(radius_mi / earth_radius_mi) * math.cos(bearing_rad)
        )

        new_lon = start_lon + math.atan2(
            math.sin(bearing_rad) * math.sin(radius_mi / earth_radius_mi) * math.cos(start_lat),
            math.cos(radius_mi / earth_radius_mi) - math.sin(start_lat) * math.sin(new_lat)
        )
        
        points.append((math.degrees(new_lon), math.degrees(new_lat)))
    
    return points


def retrieve_bb(img, object_class, fields_to_search, client, index_name):
    
    
    bbboxes = []
    bb_field = fields_to_search[ 'bb_field']
    # print(f"bb_field == {bb_field} \t object_class == {object_class}")
    
    # run this to get the first object before adding numbers to subsequent ones
    if object_class in bb_field:
        # print("old", bb_field)
        obj_name_len = len(object_class)
        
        obj_name_loc = bb_field.find(object_class)
        obj_name_idx_end = obj_name_loc + (obj_name_len)
        cur_obj_name = bb_field[obj_name_loc:obj_name_idx_end]
        new_bb_field = bb_field.replace(cur_obj_name, f'{cur_obj_name}')
        # print("old bb_field", bb_field)
        # print("new bb_field", new_bb_field)
        first_dot = new_bb_field.find('.')
        cur_img_name = img
        first_dot = new_bb_field.find('.')
        new_bb_field = cur_img_name+new_bb_field[first_dot:]
        # print('new fielddddddd', new_bb_field)
        # print('cur_img_name = ====', cur_img_name)
        # print('bbboxesssss', bbboxes)
        # query_for_bb_val = {
        #     "query": {
        #         "match_all": {}
        #     },
        #     "_source": [new_bb_field]
            
        # }
        # bb_values = client.search(index=index_name, body=query_for_bb_val)
        # print("bb_values", bb_values)
        # print(f'cur_obj_name_idx ++ {cur_obj_name}')
        assertion_switch = 0 
        search_on_of = 0
        # for hit in bb_values['hits']['hits']:
        #     try:
        #         assert len(hit['_source'].keys()) != 0
        #         bb = hit['_source'][f'{cur_img_name}']['img_insights']['class_conf_bb_seg'][f'{cur_obj_name}'][0]['bb']
        #         # print("yes", bb)
        #         bbboxes.append(bb)
        #     except AssertionError as e:
        #         pass
        #         # print('assertion error', e)
        print(f"new_bb_field *** {new_bb_field}")
        for idx in range(0, 6):
            cur_obj_name = cur_obj_name
            if idx != 0:
                cur_obj_name = f"{cur_obj_name}_{idx}"
                
            new_bb_field = bb_field.replace(cur_obj_name, f'{cur_obj_name}')
            print(f"new bb field ++ {new_bb_field} \t idx == {idx} --- curobjname -- {cur_obj_name}")
            # print("old bb_field", bb_field)
            # print("new bb_field", new_bb_field)
            first_dot = new_bb_field.find('.')
            cur_img_name = new_bb_field[:first_dot]
            # print('cur_img_name = ', cur_img_name)
            query_for_bb_val = {
                "query": {
                    "match_all": {}
                },
                "_source": [new_bb_field]
                
            }
            bb_values = client.search(index=index_name, body=query_for_bb_val)
            # print(f"++ bb_values\n ++++ {bb_values} +++")
            # print("bb_values", bb_values)
            # print(f'cur_obj_name_idx =+ {cur_obj_name}_{idx}')
            #if assertion switch is greater than 2 is means that the index to the object is finished
            # print(f"++ bb_values['hits']['hits'] \n ++++ {bb_values['hits']['hits']} +++")
            # for hit in bb_values['hits']['hits']:
            #     # print(f"=={cur_obj_name} \n {hit}==")
            #     try:
            #         assert len(hit['_source'].keys()) != 0
            #         # print('idxxxx', idx)
            #         bb = hit['_source'][f'{cur_img_name}']['img_insights']['class_conf_bb_seg'][f'{cur_obj_name}'][0]['bb']
            #         bbboxes.append(bb)
            #         # print("yes", bb)
            #     except AssertionError as e:
            #         # print('assertion error', e)
            #         assertion_switch += 1
            
            # if assertion_switch == 3:
            #     # print('assertion switch', assertion_switch)
            #     search_on_of += 1
            #     # print('search_on_of', search_on_of)
            # if search_on_of >= 3:
            #     print("finished")
                
    # print("bbboxes", bbboxes)
    return bbboxes

def euclidean_dist(search_query, imgs_lat_long):
    # print("keeeeysss", imgs_lat_long.keys())
    # print("img latyyy long", imgs_lat_long)
    user_lat = float(search_query['latitude'])
    user_long = float(search_query['longitude'])
    user_radius = float(search_query['radius'])
    # close_imgs_id = {'img_ids':[],
    #                  'img_names': [],
    #                  'object': search_query['object']}
    object_name = search_query['object']
    close_imgs_id = {}
    close_imgs_name = []
    
    for img_id, bb_lat_long in imgs_lat_long.items():
        cur_img_id = img_id
        cur_img_name = bb_lat_long['lat_long']['cur_img_name']
        # print("Image name for l2dist", cur_img_name)
        cur_img_lat = float(bb_lat_long['lat_long']['latitude'])
        cur_img_long = float(bb_lat_long['lat_long']['longitude'])

        distance = math.sqrt(((user_lat - cur_img_lat)**2 + (user_long - cur_img_long)**2))
        
        if distance < user_radius:
            close_imgs_id.setdefault(cur_img_id, {})
            close_imgs_id[cur_img_id].setdefault('bb', bb_lat_long['bb'])
            close_imgs_id[cur_img_id].setdefault('img_name', cur_img_name)
            close_imgs_id[cur_img_id].setdefault('object', object_name)
            
            
            
    return close_imgs_id

def extract_img_objs_bb(img_name, object_id, downloaded_imgs, close_imgs_id, base_dir):
    """
        for hit in lat_long_fields['hits']['hits']:
        if len(hit['_source'].keys()) != 0:
            bb = hit['_source']['IMG_1943']['img_insights']['class_conf_bb_seg']['person_1'][0]['bb']
            print("yes", bb)
    
    """
    # print("object_idobject_id", object_id)
    img_name_with_extention = object_id+'.jpg'
    img_index = downloaded_imgs.index(img_name_with_extention)
    img_frm_down_imgs = downloaded_imgs[img_index]
    cur_img_full_path = os.path.join(base_dir, img_frm_down_imgs)
    cur_img_bb = close_imgs_id['bb']
    
    read_cur_img = cv2.imread(cur_img_full_path)
    height, width, _ = read_cur_img.shape
   
    color = (0, 255, 0)
    thickness = 3
    for bb in cur_img_bb:
        x_min = bb[0]
        y_min = bb[1]
        x_max = bb[2]
        y_max = bb[3]
        cv2.rectangle(read_cur_img , (x_min, y_min), (x_max, y_max), color, thickness)
        # new_img_name = os.path.join(base_dir, str(idx))
        cv2.imwrite(cur_img_full_path, read_cur_img)

    
    
    # cur_img = os.path.join(img_dir, f'{img_name}.jpg')
    # read_cur_img = cv2.imread(cur_img)
    # height, width, _ = read_cur_img.shape
    # print("height and width", height, width)


def extract_image_meta_data(image_metadata_dir, img, **kwargs):
    image_files = os.listdir(image_metadata_dir)
    # img_files = Image.open(image)
    image_tags_context = {} #change the list to dictionary with the key as the image name
    # for image in image_files:
    meta_data = {}
    img_insight = {}
    new_metrics = {}
    
    image_full_path = os.path.join(image_metadata_dir, img)
    image_name = img.split('.')[0]
    img_dim = cv2.imread(image_full_path)
    height, width, _ = img_dim.shape
    img_area = width * height
    caller = "meta_data_api"
    request= kwargs['request']
    # image_file_path = path to the currently saved image
        
    opened_image = Image.open(image_full_path)
    # print("the image: ", image_full_path, os.path.isfile(image_full_path))
    exif_data = opened_image._getexif()
    # print("image full path", image_full_path)
    
    if exif_data is not None:
        # print("image full path", image_full_path)
        img_insights, class_names_count = handle_meta_data_api_obj_det(image_full_path, img_area)
        image_tags = {}
        for tag, value in exif_data.items():
            if tag in TAGS and TAGS[tag] != 'MakerNote':
                # print(f"tag: {TAGS[tag]} , value: {value}")
                if TAGS[tag] == "GPSInfo":
                    # print(f"image_tags[TAGS[tag]] = {str(value)}")

                    lat_hemispher = value[1]

                    long_hemispher = value[3]
                    lat_tupple = value[2]
                    long_tupple = value[4]

                    
                    latitude = convert_to_dec_degrees(lat_tupple, lat_hemispher)
                    longitude = convert_to_dec_degrees(long_tupple, long_hemispher)
                    

                    image_tags[TAGS[tag]]= {}
                    image_tags[TAGS[tag]]['latitude'] = float(latitude)
                    image_tags[TAGS[tag]]['longitude'] = float(longitude) 
                elif TAGS[tag] == "DateTime":
                    image_tags[TAGS[tag]] = str(value)
        
        image_tags.setdefault('img_dimensions', {})
        image_tags['img_dimensions'].setdefault('width', width)
        image_tags['img_dimensions'].setdefault('height', height)
        # print("image name type", type(image_name))
        image_tags_context[image_name] = {}
        
        image_tags_context[image_name].setdefault('metadata', image_tags)
        image_tags_context[image_name].setdefault('img_insights', img_insights)
            

    json_context = json.dumps(image_tags_context)
    class_names_count = {**class_names_count}
    
    new_metrics.setdefault('detections', class_names_count)
    new_metrics.setdefault('metadata', image_tags_context[image_name]['metadata'])

    return image_tags_context, new_metrics

def delete_dir_contents(directory_path):
    for parent_dir, sub_dirs, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(parent_dir, file)
            os.remove(file_path)
        
        # code to delete sub directories


def save_to_s3_meta_data(bucket_name, file_path, doc_id):
    s3 = session.resource('s3')
    response = s3.Bucket(bucket_name).upload_file(file_path, doc_id)

def img_insight_to_json(insights_obj, bucket_name, json_insight_dir, img_name, doc_id):
    cur_img = os.path.join(json_insight_dir, f'{img_name}.json')
    json_obj = json.dumps(insights_obj, indent=1)

    with open(cur_img, 'w') as output_file:
        output_file.write(json_obj)
    
    
    s3 = session.resource('s3')
    response = s3.Bucket(bucket_name).upload_file(cur_img, f'img-metrics/{doc_id}.json')

def read_img_wt_bb(imgs_path):
    imgs_full_path = []

    for img in os.listdir(imgs_path):
        img = img.split('.')[0]
        imgs_full_path.append(img)
    return imgs_full_path


import pandas as pd
import cv2
import numpy as np
import os
import csv
import boto3
import glob
# from ultralytics import YOLO

from .utils import create_csv
from .yolo import draw_box_and_save_image
from pages.utils_segmentation import handle_meta_data_api_obj_det

parent_dir = os.getcwd()
media = os.path.join(parent_dir, 'media')
test_images_dir = os.path.join(media, 'test_images')
test_csv_dir = os.path.join(media, 'test_csv')
aws_result = os.path.join(media, 'result_aws')
csv_for_scores = os.path.join(media, 'csv_for_scores')


cred_pad = '/Users/prynet/Documents/aws_cred/emeka_accessKeys.csv'
df = pd.read_csv(cred_pad)
#print(df.columns)
access_key_id = df.loc[df.index[0], 'Access key ID'] #df.index[0] returns first row, second argument is the column name 

secret_key_id = df.loc[df.index[0], 'Secret access key']

client = boto3.client('rekognition',
                        aws_access_key_id = access_key_id,
                        aws_secret_access_key = secret_key_id, region_name='us-east-1') # creating an aws client 
        


def aws_client(cred_pad):
    pass
    # print(os.path.isfile(cred_pad))


def aws_read_images(test_images_dir, term):
    print("Running AWS Detect ==>")
    print("termoooo", term)
    aws_boxes_csv = os.path.join(csv_for_scores, 'aws_boxes.csv')
    image_list = glob.glob(f"{test_images_dir}/*.jpg")
    # print("image list", image_list)
    object_insights = {}
    if term == 'meta_data_api':
        current_image = test_images_dir
        context = handle_meta_data_api_obj_det(current_image)
        return context

            
    else:
    
        for img in image_list:
            boxes = []
            confidences = []
            class_ids = []
            my_img = cv2.imread(img)
            image_name = os.path.basename(img).split('.')[0]
            height, width, _ = my_img.shape
            # print('height and width', height, width)
            
            with open(img, 'rb') as image_file: #aws expects the image as a byte file, this is what this line does
                source_byte = image_file.read()
                response = client.detect_labels(
                    Image={'Bytes': source_byte},
                    MaxLabels=10,
                    MinConfidence=70
                )
            
            for label in response['Labels']:
                if label['Name'] == 'Person':
                    for detection in label['Instances']:
                        confidences.append(detection['Confidence']/100)
                        x = int(detection['BoundingBox']['Left'] * width)
                        y = int(detection['BoundingBox']['Top'] * height)
                        wt = int(detection['BoundingBox']['Width'] * width)
                        ht = int(detection['BoundingBox']['Height'] * height)
                        boxes.append([x, y, wt, ht])
                        class_ids.append(0)
                        # print(detection['Confidence'])
                        # print(detection['BoundingBox']['Width'])
                        # print(detection['BoundingBox']['Height'])
                        # print(detection['BoundingBox']['Top'])
                        # print(detection['BoundingBox']['Left'])
            draw_box_and_save_image(my_img, boxes, confidences, image_name, height, width, aws_boxes_csv, term, class_ids)
            #print(type(response['Labels']))
            # for res in response.items():
            #     print(len(res.keys()))
                # if label['Name'] == 'Person':
                    # print(label['Name'])
                    # print(label['Confidence'])
                    # print(label['Instances'][0]['BoundingBox'])
            # for k,v in response.items():
            #     print(f"key: \t {k} === value: \t {v}")
            #     # print(os.path.basename(img))


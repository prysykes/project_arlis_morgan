import os
import pandas as pd
import json
import csv
from django.shortcuts import render
from django import forms
from django.http import HttpResponse, JsonResponse, HttpRequest
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status
from rest_framework.renderers import TemplateHTMLRenderer

from .elastic_search_utils import insert_into_aws_opensearch, search_opensearch_handler

#clea cache:
from django.core.cache import cache

from nlp.utils import run_jobs
# from vision.views import run_detection

from .serializers import ObjectDetectionSerializer, NLPSerializer, ImageMetaDataSerializer
from .utils import generate_api_response, extract_image_meta_data, delete_dir_contents, save_to_s3_meta_data, img_insight_to_json

#for getting all the registered users
from django.contrib.auth import get_user_model
parent_dir = os.getcwd()
csv_for_scores_dir = os.path.join(parent_dir, 'media', 'csv_for_scores')
image_metadata_dir = os.path.join(parent_dir, 'media', 'img_for_metadata')
json_insight_dir = os.path.join(parent_dir, 'media', 'json_insight_dir')



# User = get_user_model()


# generate_api_response(csv_for_scores_dir)



class ObjectDetectionView(APIView):
    serializer_class = ObjectDetectionSerializer 
    csv_for_scores_dir = os.path.join(parent_dir, 'media', 'csv_for_scores')
    #overwrite default get and post method
    def get(self, request):
        # users = User.objects.all().values()
        return Response("get called")
        #return Response({"all users": serializers. users})

    def post(self, request):
        serializer_obj = ObjectDetectionSerializer(data=request.data)
        

        if(serializer_obj.is_valid()):
            serializer_obj.save()
        #next step call the functions 
        # for aws and yolo to read the images and make inference
        
        # setattr(request, 'term_api', 'yolo-aws')
        #run_detection(request, caller='yolo-aws')
        api_response = generate_api_response(csv_for_scores_dir)
        return Response(api_response)

class NLPView(APIView):
    serializer_class = NLPSerializer

    def get(self, request):
        return Response("get called")
    
    def post(self, request):
        serializer_obj = NLPSerializer(data=request.data)

        if(serializer_obj.is_valid()):
            serializer_obj.save()
        
        context = run_jobs(caller='api')
        
        
        return Response(context)

class ImageMetaDataView(APIView): #TODO: call object detection on the images 
    cache.clear()
    serializer_class = ImageMetaDataSerializer

    def get(self, request):
        # print("get call")
        data = request.data
        print("data", len(data))
        user = request.user
        if len(data) != 0:
            search_opensearch_handler(user, data)        
        # print(request)
        return Response("jh")
    
    def post(self, request):
        bucket_name = 'img-processing-bucket'
        print("post called")
        username = request.user
        search_index = request.data.get('search_index')
        serializer_obj = ImageMetaDataSerializer(data=request.data)
        # print("Meta data", search_index)
        if (serializer_obj.is_valid()):
            image_inisght = serializer_obj.save()
        uploaded_img_files = os.listdir(image_metadata_dir)
        for img_file in uploaded_img_files:
            current_img_full_path = os.path.join(image_metadata_dir, img_file)
            context, new_metrics = extract_image_meta_data(image_metadata_dir, img_file, request=request)
            # print(f" class_names_count, {new_metrics}")
            json_object = json.dumps(context, indent=2)
            doc_id = insert_into_aws_opensearch(username, json_object, search_index)
            img_insight_to_json(new_metrics, bucket_name, json_insight_dir, img_file, doc_id)
            save_to_s3_meta_data(bucket_name, current_img_full_path, doc_id)
        delete_dir_contents(image_metadata_dir)
        delete_dir_contents(json_insight_dir)
        
        
        # print(type(context))

        return Response(context)
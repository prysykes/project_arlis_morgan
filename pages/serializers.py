import os
import jsonfield
from rest_framework import serializers, renderers

# from vision.views import run_detection
from django.core.files.storage import default_storage #helps specify the folver for the uploaded files
# from . utils import save_to_s3_meta_data


bucket_name = 'img-processing-bucket'

parent_dir = os.getcwd()
media = os.path.join(parent_dir, 'media')
test_images_dir = os.path.join(media, 'test_images')
test_csv_dir = os.path.join(media, 'test_csv')
img_for_metadata_dir = os.path.join(media, 'img_for_metadata')
nlp_csv_file_dir = os.path.join(media, 'nlp_csv')

image_metadata_dir = os.path.join(parent_dir, 'media', 'img_for_metadata')


class CustomStyles(renderers.TemplateHTMLRenderer):
    def get_template_context(self, data, renderer_context):
        context = super().get_template_context(data, renderer_context)
        context['my_cont'] = True
        return context

class ObjectDetectionSerializer(serializers.Serializer):
   
    test_images_file_1 = serializers.FileField(allow_null=True)
    test_images_file_2 = serializers.FileField(allow_null=True)
    test_images_file_3 = serializers.FileField(allow_null=True)
    test_images_file_4 = serializers.FileField(allow_null=True)
    test_images_file_5 = serializers.FileField(allow_null=True)
    test_csv_file = serializers.FileField(allow_null=True)

    def validate(self, data):
        #apply any validation here like length check etc
        #test_images_file = data.get('test_images_file')
        test_images_file_1 = data.get('test_images_file_1')
        test_images_file_2 = data.get('test_images_file_2')
        test_images_file_3 = data.get('test_images_file_3')
        test_images_file_4 = data.get('test_images_file_4')
        test_images_file_5 = data.get('test_images_file_5')
        test_csv_file = data.get('test_csv_file')
        

        return data #this is a dictionary accessed in the save method below


    def save(self, **kwargs):
        
        image_paths = []
        for file in self.validated_data.values():
            if file:

                file_name = file.name 
                current_file_extention = file_name.split('.')[1]
                if current_file_extention != 'csv':
                    image_path = default_storage.save(test_images_dir + "/" +file_name, file)
                else:
                    image_path = default_storage.save(test_csv_dir + "/" +file_name, file)
                #changes the default storage for this view
                #print("image path", image_path)
                image_paths.append(image_path)
        
        return image_paths
        

class NLPSerializer(serializers.Serializer):
    csv_file_upload = serializers.FileField(allow_null=True)


    def validate(self, data):
        csv_file_upload = data.get('csv_file_upload')

        return data
    
    def save(self, **kwargs):
        # csv_file = self.validated_data.values()
        for file in self.validated_data.values():
            if file:
                file_name = file.name
                print("File Name: ", file_name)
                file_name_with_path = os.path.join(nlp_csv_file_dir, file_name )
                csv_file_path = default_storage.save(file_name_with_path, file)

        
        

        return csv_file_path


class ImageMetaDataSerializer(serializers.Serializer):
    search_index = serializers.CharField(max_length=20, style={'input_type': 'text', 'width': '20px'})
    uploaded_image_1 = serializers.FileField(allow_null=True)
    uploaded_image_2 = serializers.FileField(allow_null=True)
    uploaded_image_3 = serializers.FileField(allow_null=True)

    def validate(self, data):
        uploaded_image_1 = data.get('uploaded_image_1')
        uploaded_image_2 = data.get('uploaded_image_2')
        uploaded_image_3 = data.get('uploaded_image_3')

        return data

    def save(self, **kwargs):
        for image in self.validated_data.values():
            if not isinstance(image, str):
                image_name = image.name
                print("Image File Name: ", image_name)
                image_name_with_path = os.path.join(img_for_metadata_dir, image_name)
                
                image_file_path = default_storage.save(image_name_with_path, image)
                # save_to_s3(bucket_name, image_name_with_path)
                print("image file path", image_file_path)
                print("image_name_with_path", image_name_with_path)
                
        return "img_insights"
from distutils.command.upload import upload
from tabnanny import verbose
from django.db import models
import os

# Create your models here.
parent_dir = os.getcwd().lstrip('/')
media = os.path.join(parent_dir, 'media')
test_images_dir = os.path.join(media, 'test_images')
test_csv_dir = os.path.join(media, 'test_csv')


class TempTestImagesCSV(models.Model):
    test_images_file = models.FileField(upload_to=test_images_dir, null=True, blank='True')
    test_csv_file = models.FileField(upload_to=test_csv_dir, null=True, blank=True,)
    
    def __str__(self):
        return "Test_Images"


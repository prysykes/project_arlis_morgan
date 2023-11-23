from distutils.command.upload import upload
from tabnanny import verbose
from django.db import models
import os

# Create your models here.
parent_dir = os.getcwd().lstrip('/')
media = os.path.join(parent_dir, 'media')
nlp_csv_dir = os.path.join(media, 'nlp_csv')

print('parent', parent_dir)
print('csv', nlp_csv_dir)

class NLPCSV(models.Model):
    uploaded_nlp_csv = models.FileField(upload_to=nlp_csv_dir, null=True, blank=True)
    
    def __str__(self):
        return "NLP CSV"

#j
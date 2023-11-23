from django.db import models
from django.contrib.auth.models import User


class IAMRole(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role_arn = models.CharField(max_length=255)
    role_name = models.CharField(max_length=255, unique=True)

class NotebookInstance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    instance_name = models.CharField(max_length=255, unique=True)
    instance_arn = models.CharField(max_length=255)
    
    instance_type = models.CharField(max_length=255)     
   
    instance_status = models.CharField(max_length=255)
    instance_url = models.URLField(max_length=255, null=True, blank=True)
    start_time = models.DateTimeField(null=True, blank=True)

class Predictions(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/')
    prediction = models.TextField()
    predicted_label = models.CharField(max_length=100)
   
class Training(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    dataset_metadata = models.JSONField(null=True, blank=True)
    model_dir = models.CharField(max_length=255)
    model_summary = models.TextField(null=True, blank=True)
    training_status = models.CharField(max_length=255, default='Not Started')
   

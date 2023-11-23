from django.contrib import admin
from mltraining.models import IAMRole, NotebookInstance, Predictions, Training

# Register your models here.
admin.site.register(IAMRole)
admin.site.register(NotebookInstance)
admin.site.register(Predictions)
admin.site.register(Training)

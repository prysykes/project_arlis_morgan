from django.urls import path
# from . import views
from .views import vision_app, upload_images_csv, view_uploaded_images, view_bar_plot, read_yolo_result, read_aws_result, f1_score, evaluate_performance

urlpatterns = [
    path('', vision_app, name='vision_app'),
    path('vision/upload_images_csv', upload_images_csv, name='upload_images_csv'),
    path('vision/view_uploaded_images', view_uploaded_images, name='view_uploaded_images'),
    path('vision/view_bar_plot', view_bar_plot, name='view_bar_plot'),
    # path('vision/run_detection/term', run_detection, name='run_detection'),
    path('vision/evaluate_performance/term', evaluate_performance, name='evaluate_performance'),
    path('vision/read_yolo_result', read_yolo_result, name='read_yolo_result'),
    path('vision/read_aws_result', read_aws_result, name='read_aws_result'),
    path('vision/f1_score', f1_score, name='f1_score'),
    
]
from django.urls import path
from . import views


urlpatterns = [
    path('', views.nlp_app, name='nlp_app'),
    path('upload_nlp_csv', views.upload_nlp_csv, name='upload_nlp_csv'),
    path('view_uploaded_csv', views.view_uploaded_csv, name='view_uploaded_csv'),
    path('run_analysis', views.run_analysis, name='run_analysis')
    
]
#j
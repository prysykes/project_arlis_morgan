from django.urls import path
from . import views


urlpatterns = [
    path('', views.mltraining, name='mltraining'),
    path('launch_instance/', views.launch_instance, name='launch_instance'),
    path('delete_instance', views.delete_instance, name='delete_instance'),
    path('upload_file', views.upload_file, name='upload_file'),
    path('classify_images', views.classify_images, name='classify_images'),
    path('upload_dataset', views.upload_dataset, name='upload_dataset'),
    path('open_jupyterlab', views.open_jupyterlab, name='open_jupyterlab')


    # path('upload_jupyter_notebook', views.upload_jupyter_notebook, name='upload_jupyter_notebook'),
    # path('launch_notebook', views.launch_notebook, name='launch_notebook')
]
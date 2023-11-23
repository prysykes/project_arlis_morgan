from django.urls import path
from . import views


urlpatterns = [
    path('search_dataset', views.search_dataset, name='search_dataset'),
    path('download_dataset/term', views.download_dataset, name='download_dataset'),
    path('dataset_list', views.dataset_list, name='dataset_list'),
    path('downlaod_dataset_uci', views.downlaod_dataset_uci, name='downlaod_dataset_uci'),
    path('view_dataset_kaggle', views.view_dataset_kaggle, name='view_dataset_kaggle'),
    path('view_dataset_uci', views.view_dataset_uci, name='view_dataset_uci')
    
]
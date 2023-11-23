from django.urls import path
from . import views

# from . import api_views

from .api_views import ObjectDetectionView, NLPView, ImageMetaDataView
# from .api_views import NLPView


urlpatterns = [
    path('', views.index, name='index'),
    path('object_detection_endpoint/', ObjectDetectionView.as_view(), name='object_detection_endpoint'),
    path('nlp_analysis_endpoint/', NLPView.as_view(), name='nlp_endpoint'),
    path('image_metadata_endpoint/', ImageMetaDataView.as_view(), name='image_metadata_endpoint'),
    path('elastic_search', views.elastic_search, name='elastic_search'),
    path('search_opensearch', views.search_opensearch, name='search_opensearch'),
    # path('object_detection_api_view/', ObjectDetectionApView.as_view()),
    
]
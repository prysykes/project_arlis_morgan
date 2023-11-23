from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pages.urls')),
    path('datasetsearch/', include('datasetsearch.urls')),
    path('registration/', include('registration.urls')),
    path('vision/', include('vision.urls')),
    path('nlp/', include('nlp.urls')),
    path('mltraining/', include('mltraining.urls')),
    # path('oidc/', include('mozilla_django_oidc.urls')),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
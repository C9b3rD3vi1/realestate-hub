
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# The URL configuration for the Django project
# This file defines the URL patterns for the project, including the admin interface

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('listings.urls')),
]

# The URL patterns for serving media and static files in development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


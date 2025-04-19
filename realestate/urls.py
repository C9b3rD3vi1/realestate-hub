
from django.contrib import admin
from django.urls import path, include

# The URL configuration for the Django project
# This file defines the URL patterns for the project, including the admin interface

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('listings.urls')),
]

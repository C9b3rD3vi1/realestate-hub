from django.urls import path, include

from . import views
# The URL configuration for the listings app
# This file defines the URL patterns for the listings app, including the home page and the listing detail page


urlpatterns = [
    path('', views.home, name='home'),  # The home page of the listings app
    path('listing/', views.listing, name='listing'),  # The detail page for a specific listing
    path('register/', views.user_register, name='register'),  # User registration page
]
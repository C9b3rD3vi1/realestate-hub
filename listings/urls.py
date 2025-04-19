from django.urls import path, include
from .views import *

# The URL configuration for the listings app
# This file defines the URL patterns for the listings app, including the home page and the listing detail page


urlpatterns = [
    path('', home, name='home'),  # The home page of the listings app
    path('listing/<int:listing_id>/', listing, name='listing'),  # The detail page for a specific listing
]
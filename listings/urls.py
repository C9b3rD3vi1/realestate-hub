from . import views
from django.urls import path, include


# The URL configuration for the listings app
# This file defines the URL patterns for the listings app, including the home page and the listing detail page


urlpatterns = [
    path('', views.home, name='home'),  # The home page of the listings app
    path('listing/', views.listing, name='listing'),  # The detail page for a specific listing
    path("listings/<slug:slug>/", views.listing_detail, name="listing_detail"),
    path('register/', views.user_register, name='register'),  # User registration page
    path('login/', views.user_login, name='login'),  # User login page
    path('logout/', views.user_logout, name='logout'),  # User logout page
    path('contact/', views.contact, name='contact'),  # Contact page
    path('profile/', views.user_profile, name='profile'),  # User profile page
    #path('profile/view/', views.profile_detail_view, name='profile_detail'),

    #path('password_reset/', views.password_reset, name='password_reset'),  # Password reset page
   # path('password_reset/done/', views.password_reset_done, name='password_reset_done'),  # Password reset done page
    #path('reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),  # Password reset confirm page
    #path('reset/done/', views.password_reset_complete, name='password_reset_complete'),  # Password reset complete page
    path('about/', views.about, name='about'),  # About page
    
    
    path('house/<slug:slug>/', views.housing_detail, name='housing_detail'),
    path('car/<slug:slug>/', views.car_detail, name='car_detail'),
    path('land/<slug:slug>/', views.land_detail, name='land_detail'),
    
    path('listCategory/<str:category>/', views.category_listings, name='category_listings'),
    
     path('subscribe/', views.subscribe_newsletter, name='subscribe_newsletter'),
     
     path('car/<int:car_id>/favorite/', views.favorite_car, name='favorite_car'),
     #path('car/<int:car_id>/test-drive/', views.book_test_drive, name='book_test_drive'),


]
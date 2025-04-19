from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic
from .forms import *
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required


# Create your views here.
def home(request):
    # This view renders the home page of the listings app
    return render(request, 'home.html')


def listing(request):
    # This view renders the detail page for a specific listing
    # The listing_id parameter is used to retrieve the specific listing from the database
    return render(request, 'listings.html')


# User registration and creation, authentication form
def user_register(request):
    # This view handles user registration
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})


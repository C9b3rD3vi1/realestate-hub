from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic
from .forms import *
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
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




# User login and authentication functionality
def user_login(request):
    # This view handles user login
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        # Validate the form data
        if form.is_valid():
            # Get the cleaned data from the form
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            # Authenticate the user
            user = authenticate(username=username, password=password)
            if user is not None:
                # If the user is authenticated, log them in
                login(request, user)
                # Redirect to the home page
                return redirect('home')
    else:
        # If the request method is GET, create an empty form
        form = AuthenticationForm(request)
    return render(request, 'login.html', {'form': form})



def contact(request):
    # This view handles contact form submissions
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Get the cleaned data from the form
            name = form.cleaned_data.get('name')
            email = form.cleaned_data.get('email')
            message = form.cleaned_data.get('message')
            # Send the email
            send_mail(
                'Contact Form Submission',
                f'Name: {name}\nEmail: {email}\nMessage: {message}',
                'noreply@example.com',
                ['admin@example.com'],
                fail_silently=False,
            )
            # Redirect to the contact page with a success message
            return redirect('contact')
    else:
        # If the request method is GET, create an empty form
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})



def about(request):
    # This view displays information about the website
    return render(request, 'about.html')

def terms(request):
    # This view displays the terms and conditions of the website
    return render(request, 'terms.html')

def privacy(request):
    # This view displays the privacy policy of the website
    return render(request, 'privacy.html')

def faq(request):
    # This view displays frequently asked questions
    return render(request, 'faq.html')




from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic
from .forms import *
from django.http import Http404
from django.db.models import Q
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from urllib.parse import urlencode

from .models import LandProperties, CarProperties, HousingProperties


# Create your views here.
def home(request):
    # This view renders the home page of the listings app
    return render(request, 'home.html')


def listing(request):
    query = request.GET.get('q')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort = request.GET.get('sort', '-created_at')

    is_filtered = any([
        query, min_price, max_price, sort not in ['', '-created_at']
    ])

    if is_filtered:
        # Handle filtered results: default to Land
        model_map = {
            'land': LandProperties,
            'housing': HousingProperties,
            'car': CarProperties,
        }
        type = request.GET.get('type', 'land')
        model = model_map.get(type, LandProperties)

        queryset = model.objects.filter(is_available=True)

        if query:
            queryset = queryset.filter(Q(title__icontains=query) | Q(location__icontains=query))
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if sort:
            queryset = queryset.order_by(sort)

        paginator = Paginator(queryset, 12)
        page_number = request.GET.get("page")
        listings = paginator.get_page(page_number)

        return render(request, "listings.html", {
            "filtered": True,
            "listings": listings,
            "type": type
        })

    # If no filters — show all 3 types in sections
    land_listings = LandProperties.objects.filter(is_available=True)[:8]
    housing_listings = HousingProperties.objects.filter(is_available=True)[:8]
    car_listings = CarProperties.objects.filter(is_available=True)[:8]

    return render(request, "listings.html", {
        "filtered": False,
        "land_listings": land_listings,
        "housing_listings": housing_listings,
        "car_listings": car_listings,
    })

def listing_detail(request, slug):
    listing = None
    listing_type = None

    for model, name in [(CarProperties, 'Car'), ( HousingProperties, 'House'), (LandProperties, 'Land')]:
        try:
            listing = model.objects.get(slug=slug)
            listing_type = name
            break
        except model.DoesNotExist:
            continue

    if not listing:
        raise Http404("Property not found.")

    return render(request, 'listing_detail.html', {
        'listing': listing,
        'listing_type': listing_type,
    })


def housing_detail(request, slug):
    house = get_object_or_404(HousingProperties, slug=slug)
    return render(request, "housing_detail.html", {"house": house})

def land_detail(request, slug):
    land = get_object_or_404(LandProperties, slug=slug)
    return render(request, "land_detail.html", {"land": land})

def car_detail(request, slug):
    car = get_object_or_404(CarProperties, slug=slug)
    return render(request, "car_detail.html", {"car": car})


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

def user_logout(request):
    # handle user logout request
    if request.method == 'POST':
        logout(request)
        return redirect('home')


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
            '''
            send_mail(
                'Contact Form Submission',
                f'Name: {name}\nEmail: {email}\nMessage: {message}',
                'noreply@example.com',
                ['admin@example.com'],
                fail_silently=False,
            )'''
            # Redirect to the contact page with a success message
            return redirect('contact')
    else:
        # If the request method is GET, create an empty form
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})


'''


# password reset
def password_reset(request):
    # This view handles password reset requests
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            # Get the cleaned data from the form
            email = form.cleaned_data.get('email')
            # Send the password reset email
            send_mail(
                'Password Reset Request',
                f'Click the link below to reset your password:\n\nhttp://example.com/reset-password/{email}',
                'noreply@example.com',
                [email],
                fail_silently=False,
            )
            # Redirect to the password reset page with a success message
            return redirect('password_reset')
    else:
        # If the request method is GET, create an empty form
        form = PasswordResetForm()
    return render(request, 'password_reset.html', {'form': form})
'''


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

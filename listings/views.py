from .forms import *
from django.db.models import Q
from django.views import generic
from django.http import Http404, JsonResponse
from itertools import chain
from django.utils import timezone
from urllib.parse import urlencode
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .forms import BookingForm, ContactAgentForm
from .models import Amenity, HousePropertiesImage, LandPropertiesImage, CarPropertiesImage, NeighborhoodFeature, RentalHouse, Favorite
from .models import LandProperties, CarProperties, HousingProperties, Profile, Testimonials, PropertyTestimonialHouse
from .models import NewsletterSubscriber, FAQ, PriceHistoryHouse, PriceHistoryCar, PriceHistoryLand, PropertyTestimonialCar, PropertyTestimonialLand



# Create your views here.
def home(request):
    houses = HousingProperties.objects.filter(is_available=True)[:8]
    lands = LandProperties.objects.filter(is_available=True)[:8]
    cars = CarProperties.objects.filter(is_available=True)[:8]
    testimonials = Testimonials.objects.all()[:8]
    faqs = FAQ.objects.filter(is_active=True)


     # Fetch featured items from each model
    featured_houses = HousingProperties.objects.filter(is_featured=True)
    featured_lands = LandProperties.objects.filter(is_featured=True)
    featured_cars = CarProperties.objects.filter(is_featured=True)

        # Merge all featured items into one queryset-like list
    featured_listings = sorted(chain(featured_houses, featured_lands, featured_cars),
        key=lambda x: getattr(x, 'created_at', None),reverse=True)

    context = {
            'houses': houses,
            'lands': lands,
            'cars': cars,
            'testimonials': testimonials,
            'faqs': faqs,
            'featured_listings': featured_listings[:10],  # limit to top 10
        }

    return render(request, 'home.html', context)


def listing(request):
    query = request.GET.get('q')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort = request.GET.get('sort', '-created_at')
    location = request.GET.get('location')
    house_type = request.GET.get('house_type')

    is_filtered = any([
        query, min_price, max_price,
        sort not in ['', '-created_at'],
        location, house_type
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
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(location__icontains=query) |
                Q(description__icontains=query)
            )
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if location:
            queryset = queryset.filter(location__icontains=location)
        if house_type and hasattr(model, 'house_type'):
            queryset = queryset.filter(house_type=house_type)
        if sort:
            queryset = queryset.order_by(sort)

        # Prefetch related data for performance
        if model in [HousingProperties, LandProperties]:
            queryset = queryset.prefetch_related('images')

        paginator = Paginator(queryset, 12)
        page_number = request.GET.get("page")
        listings = paginator.get_page(page_number)
        #
        testimonials = PropertyTestimonialHouse.objects.all()

        #
        #neighborhood = Neighborhood.objects.all()
        return render(request, "components/listings.html", {
            "filtered": True,
            "testimonials": testimonials,
            "listings": listings,
            "type": type,
            "search_query": query,
            "min_price": min_price,
            "max_price": max_price,
            "location_filter": location,
            "house_type_filter": house_type,
            "sort_option": sort,
        })


    testimonials = PropertyTestimonialHouse.objects.all()

    # If no filters — show all 3 types in sections
    land_listings = LandProperties.objects.filter(is_available=True).prefetch_related('images')[:8]
    housing_listings = HousingProperties.objects.filter(is_available=True).prefetch_related('images')[:8]
    car_listings = CarProperties.objects.filter(is_available=True)[:8]

    return render(request, "components/listings.html", {
        "filtered": False,
        "testimonials": testimonials,
        "land_listings": land_listings,
        "housing_listings": housing_listings,
        "car_listings": car_listings,
    })


# Fetch property
def category_listings(request, category=None):
    context = {}

    # Normalize input
    if category:
        category = category.lower()

    if not category or category == 'all':
        context['houses'] = HousingProperties.objects.all()
        context['lands'] = LandProperties.objects.all()
        context['cars'] = CarProperties.objects.all()
        context['category'] = 'All'
    elif category == 'house':
        context['listings'] = HousingProperties.objects.all()
        context['category'] = 'Houses'
    elif category == 'land':
        context['listings'] = LandProperties.objects.all()
        context['category'] = 'Lands'
    elif category == 'car':
        context['listings'] = CarProperties.objects.all()
        context['category'] = 'Cars'
    else:
        context['listings'] = []

    return render(request, 'home.html', context)



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

    return render(request, 'components/listing_detail.html', {
        'listing': listing,
        'listing_type': listing_type,
    })


# Fetch listing property by categories
def category_listing(request, category):
    category = category.lower()
    if category == 'house':
        listings = HousingProperties.objects.all()
    elif category == 'land':
        listings = LandProperties.objects.all()
    elif category == 'car':
        listings = CarProperties.objects.all()
    else:
        listings = []  # Or raise 404

    return render(request, 'listings/category_listing.html', {
        'listings': listings,
        'category': category.capitalize()
    })


# Fetch and handle housing details on housing_detail page
def housing_detail(request, slug):
    # Get the main house object
    house = get_object_or_404(HousingProperties, slug=slug)

    # Get neighborhood feature IDs first
    neighborhood_feature_ids = house.neighborhood.all().values_list('id', flat=True)


       # Convert size to float if it's a string
    try:
        size = float(house.size) if house.size else 0
    except (ValueError, TypeError):
        size = 0

    # Prepare all context data
    context = {
        'house': house,
        'house_images': HousePropertiesImage.objects.filter(house=house),
        'amenities': house.amenities.all(),  # Using ManyToMany relationship
        'neighborhood_features': house.neighborhood.all(),  # Using the ManyToMany relationship

        #  Fetch property testimonials
        'testimonials': PropertyTestimonialHouse.objects.filter(
            Q(property=house) | Q(property__isnull=True)
        ).order_by('-created_at')[:4],

        # Fetch price history
        'price_history': {
                    'labels': [ph.date_recorded.strftime('%b %Y') for ph in
                             house.price_history.all().order_by('date_recorded')],
                    'data': [float(ph.price) for ph in
                            house.price_history.all().order_by('date_recorded')]
                },
        # Fetch similar properties
        'similar_properties': HousingProperties.objects.filter(
            Q(neighborhood__in=neighborhood_feature_ids) |  # Use the IDs list|
            Q(house_type=house.house_type)
        ).exclude(pk=house.pk).order_by('?')[:7],
        'today': timezone.now().date(),
    }

    # Calculate price per sqm if size exists
    if size > 0:
           context['price_per_sqm'] = float(house.price) / size

    return render(request, "components/housing_detail.html", context)

def price_history_api(request, house_id):
    house = get_object_or_404(HousingProperties, id=house_id)
    price_history = house.price_history.all().order_by('date_recorded')
    return JsonResponse({
        "labels": [ph.date_recorded.strftime('%b %Y') for ph in price_history],
        "data": [float(ph.price) for ph in price_history]
    })


# Fetch and handle land details
def land_detail(request, slug):
    # Fetch land object with prefetching for efficiency
    land = get_object_or_404(
        LandProperties.objects.prefetch_related('images', 'amenities', 'neighborhood'),
        slug=slug
    )

    # Price history
    price_records = PriceHistoryLand.objects.filter(property=land).order_by('date_recorded')
    price_labels = [ph.date_recorded.strftime('%b %Y') for ph in price_records]
    price_data = [float(ph.price) for ph in price_records]

    # Testimonials
    testimonials = PropertyTestimonialLand.objects.filter(
        Q(property=land) | Q(property__isnull=True)
    ).order_by('-created_at')[:4]

    # Safely get neighborhood IDs
    neighborhood_ids = []
    if hasattr(land, 'neighborhood') and land.neighborhood:
        try:
            neighborhood_ids = land.neighborhood.values_list('id', flat=True)
        except Exception:
            neighborhood_ids = []

    # Similar properties
    similar_properties = LandProperties.objects.filter(
        Q(neighborhood__in=neighborhood_ids) | Q(land_type=land.land_type)
    ).exclude(pk=land.pk).order_by('?')[:3]

    # Price per sqm
    price_per_sqm = (land.price / land.size) if land.size else None

    context = {
        'land': land,
        'land_images': land.images.all() if hasattr(land, 'images') else [],
        'amenities': land.amenities.all() if hasattr(land, 'amenities') else [],
        'neighborhood_features': land.neighborhood.all() if hasattr(land, 'neighborhood') and land.neighborhood else [],
        'testimonials': testimonials,
        'price_history': {'labels': price_labels, 'data': price_data},
        'similar_properties': similar_properties,
        'price_per_sqm': price_per_sqm,
        'today': timezone.now().date(),
    }

    return render(request, "components/land_detail.html", context)



# Fetch car properties in details
def car_detail(request, slug):
    car = get_object_or_404(CarProperties, slug=slug)

    # Badges for car details
    badges = [
        {"label": "Make", "icon": "fa-car", "value": car.make},
        {"label": "Model", "icon": "fa-road", "value": car.model},
        {"label": "Year", "icon": "fa-calendar", "value": car.year_of_manufacture},
        {"label": "Transmission", "icon": "fa-cogs", "value": car.transmission},
        {"label": "Fuel", "icon": "fa-gas-pump", "value": car.fuel_type},
        {"label": "Mileage", "icon": "fa-tachometer-alt", "value": f"{car.mileage} km"},
    ]

    # Prepare context
    context = {
        "car": car,
        "badges": badges,
        "car_images": CarPropertiesImage.objects.filter(car=car),  # For carousel
        "amenities": car.amenities.all() if hasattr(car, 'amenities') else [],

        # Fetch testimonials (limit 4)
        "testimonials": PropertyTestimonialCar.objects.filter(
            Q(property=car) | Q(property__isnull=True)
        ).order_by('-created_at')[:4],

        # Price history for chart
        "price_history": {
            "labels": [ph.date_recorded.strftime('%b %Y') for ph in car.price_history.all().order_by('date_recorded')],
            "data": [float(ph.price) for ph in car.price_history.all().order_by('date_recorded')]
        } if hasattr(car, 'price_history') else {"labels": [], "data": []},

        # Similar cars
        "similar_cars": CarProperties.objects.filter(
            Q(make=car.make) | Q(model=car.model)
        ).exclude(pk=car.pk).order_by('?')[:7],

        "today": timezone.now().date(),
    }

    return render(request, "components/car_detail.html", context)



@login_required
def favorite_car(request, car_id):
    car = get_object_or_404(CarProperties, id=car_id)
    profile = request.user.profile
    if car in profile.favorites.all():
        profile.favorites.remove(car)
    else:
        profile.favorites.add(car)
    return redirect('/car_detail', car_id)


# User registration and creation, authentication form
def user_register(request):
    # This view handles user registration
    if request.method == 'POST':
            form = CustomUserCreationForm(request.POST, request.FILES)
            if form.is_valid():
                user = form.save()
                login(request, user)  # Optional: log in the user after registration
                messages.success(request, 'Account created successfully!')
                return redirect('home')
            else:
                messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()

    return render(request, 'components/register.html', {'form': form})


# User logout functionality requested
def user_logout(request):
    logout(request)
    return redirect('home')



# User login and authentication functionality
def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')  # prevent logged-in users from seeing login page again

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # Log the user in directly with form.get_user()
            login(request, form.get_user())
            return redirect('home')
    else:
        form = AuthenticationForm()

    return render(request, 'components/login.html', {'form': form})


# Render user profile page
@login_required
def user_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')  # stays on same page
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'components/profile.html', {'profile': profile, 'form': form})


@login_required
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
    return render(request, 'components/contact.html', {'form': form})


@require_POST
def subscribe_newsletter(request):
    email = request.POST.get('email')
    if email:
        NewsletterSubscriber.objects.get_or_create(email=email)
    return redirect(request.META.get('HTTP_REFERER', '/'))


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
    return render(request, 'components/about.html')

def terms(request):
    # This view displays the terms and conditions of the website
    return render(request, 'terms.html')

def privacy(request):
    # This view displays the privacy policy of the website
    return render(request, 'privacy.html')

def faq(request):
    # This view displays frequently asked questions
    return render(request, 'faq.html')

def add_testimonial(request):

    return render(request, 'testimonials.html')


def schedule_visit(request):

    return render(request, 'schedule_visit.html')


def rentalhouse_index(request):
    houses = RentalHouse.objects.filter(availability=True).order_by('-created_at')
    
    # Filter by search query
    query = request.GET.get('q')
    if query:
        houses = houses.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(city__icontains=query) |
            Q(address__icontains=query)
        )
    
    # Filter by house type
    house_type = request.GET.get('type')
    if house_type:
        houses = houses.filter(house_type=house_type)
    
    # Filter by amenities
    amenities = request.GET.getlist('amenities')
    if amenities:
        houses = houses.filter(amenities__id__in=amenities).distinct()
    
    # Pagination
    paginator = Paginator(houses, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    all_amenities = Amenity.objects.all()
    
    context = {
        'page_obj': page_obj,
        'all_amenities': all_amenities,
        'search_query': query or '',
        'selected_type': house_type or '',
        'selected_amenities': [int(a) for a in amenities] if amenities else [],
    }
    return render(request, 'components/rentalhouse.html', context)


# Display rental house detail on the website
def rentalhouse_detail(request, house_id):
    house = get_object_or_404(RentalHouse, id=house_id)
    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = Favorite.objects.filter(user=request.user, house=house).exists()
    
    contact_form = ContactAgentForm(initial={'house': house.id})
    booking_form = BookingForm(initial={'house': house.id})
    
    context = {
        'house': house,
        'is_favorited': is_favorited,
        'contact_form': contact_form,
        'booking_form': booking_form,
        #'map_api_key': settings.GOOGLE_MAPS_API_KEY,  # You'll need to set this up
    }
    return render(request, 'components/rentaldetail.html', context)


@login_required
def toggle_favorite(request, house_id):
    house = get_object_or_404(RentalHouse, id=house_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, house=house)
    
    if not created:
        favorite.delete()
        return JsonResponse({'status': 'removed', 'is_favorited': False})
    
    return JsonResponse({'status': 'added', 'is_favorited': True})
    
# Mark house as favorite
@login_required
def favorite_list(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('house')
    houses = [fav.house for fav in favorites]
    
    context = {
        'houses': houses,
    }
    return render(request, 'listings/favorites.html', context)

# login to contact agent
#@login_required
def contact_agent(request):
    if request.method == 'POST':
        form = ContactAgentForm(request.POST)
        if form.is_valid():
            contact = form.save()
            # Send email notification to agent (implementation depends on your email setup)
            return JsonResponse({'status': 'success', 'message': 'Your message has been sent successfully!'})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
    

# login to book rental house
@login_required
def book_house(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.save()
            return JsonResponse({'status': 'success', 'message': 'Your booking request has been submitted!'})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
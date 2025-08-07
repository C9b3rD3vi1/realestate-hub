import uuid
import requests
from django.urls import reverse
from types import LambdaType
from django.http import JsonResponse
from datetime import datetime, timedelta, timezone
from django.contrib.auth.decorators import login_required
from django.db.models.options import OrderWrt
from django.shortcuts import render, redirect
from django.shortcuts import render, get_object_or_404
from listings.models import LandProperties, CarProperties, HousingProperties, Payment, Subscription
from .forms import LandPropertyForm, HousingPropertyForm, CarPropertyForm
from .decorators import seller_or_agent_required
from django.contrib import messages
from django.conf import settings




@login_required
@seller_or_agent_required
def add_property(request):
    # Get property_type from GET or POST
    property_type = request.POST.get('property_type') or request.GET.get('property_type', '')
    form_classes = {
        'land': LandPropertyForm,
        'house': HousingPropertyForm,
        'car': CarPropertyForm,
    }

    selected_form_class = form_classes.get(property_type)
    form = selected_form_class(request.POST or None, request.FILES or None) if selected_form_class else None

    if request.method == 'POST':
        if form:
            if form.is_valid():
                property_obj = form.save(commit=False)
                property_obj.posted_by = request.user
                property_obj.save()
                messages.success(request, f"{property_type.capitalize()} property added successfully!")
                return redirect('property_list')
            else:
                messages.error(request, "There were errors in the form. Please correct them.")
        else:
            messages.error(request, "Invalid property type selected.")

    context = {
        'form': form,
        'property_type': property_type,
        'land_form': LandPropertyForm(),
        'house_form': HousingPropertyForm(),
        'car_form': CarPropertyForm(),
    }

    return render(request, 'property/addproperty.html', context)
  
  
 # Show user agent, properties dashboard with list of properties   
@login_required
#@seller_or_agent_required
def property_dashboard(request):
    user = request.user

    land_properties = LandProperties.objects.filter(owner=user)
    housing_properties = HousingProperties.objects.filter(owner=user)
    car_properties = CarProperties.objects.filter(owner=user)
    
     # Pre-fill the forms for each instance
    land_forms = {land.slug: LandPropertyForm(instance=land) for land in land_properties}
    housing_forms = {house.slug: HousingPropertyForm(instance=house) for house in housing_properties}
    car_forms = {car.slug: CarPropertyForm(instance=car) for car in car_properties}

    context = {
        'land_properties': land_properties,
        'housing_properties': housing_properties,
        'car_properties': car_properties,
        'land_forms': land_forms,
        'housing_forms': housing_forms,
        'car_forms': car_forms,
    }
    return render(request, 'property/dashboard.html', context)
 
 
 # Edit and Update Property 
@login_required
@seller_or_agent_required
def edit_property(request, category, slug):
    obj, form_class = None, None

    if category == 'land':
        obj = get_object_or_404(LandProperties, slug=slug, owner=request.user)
        form_class = LandPropertyForm
    elif category == 'housing':
        obj = get_object_or_404(HousingProperties, slug=slug, owner=request.user)
        form_class = HousingPropertyForm
    elif category == 'car':
        obj = get_object_or_404(CarProperties, slug=slug, owner=request.user)
        form_class = CarPropertyForm
    else:
        return redirect('property_dashboard')

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            return redirect('property_dashboard')  # redirect after saving
    else:
        form = form_class(instance=obj)  # prefill form with existing data

    return render(request, 'property/edit_property.html', {'form': form, 'object': obj})
    
    
# Available plans
SUBSCRIPTION_PLANS = {
    'premium': {"amount": 1000, "duration_days": 30},
    'business': {"amount": 2500, "duration_days": 90},
    'enterprise': {"amount": 5000, "duration_days": 180},
}

# Payment processing
def make_payment(request):
    if request.method == 'POST':
        plan = request.POST.get('plan')  # e.g., 'premium', 'business'
        duration = int(request.POST.get('duration', 1))  # in months

        if plan not in SUBSCRIPTION_PLANS:
            return render(request, 'payment/error.html', {"error": "Invalid plan selected."})

        base_price = SUBSCRIPTION_PLANS[plan]["amount"]
        amount = base_price * duration
        tx_ref = str(uuid.uuid4())

        payment = Payment.objects.create(
            user=request.user,
            tx_ref=tx_ref,
            amount=amount,
            plan=plan,
            status='pending',
        )

        data = {
            "tx_ref": tx_ref,
            "amount": amount,
            "currency": "KES",
            "redirect_url": request.build_absolute_uri('/payment/callback/'),
            "payment_options": "card,mpesa,banktransfer",
            "customer": {
                "email": request.user.email,
                "name": request.user.username,
            },
            "customizations": {
                "title": f"{plan.title()} Plan Payment",
                "description": f"{duration} month(s) of {plan.title()} Plan",
            },
            "meta": {
                "plan": plan,
                "duration": duration
            }
        }

        headers = {
            "Authorization": f"Bearer {settings.FLW_SECRET_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.post('https://api.flutterwave.com/v3/payments', json=data, headers=headers)

        if response.status_code == 200:
            return redirect(response.json()['data']['link'])
        else:
            return render(request, 'payment/error.html', {"error": "Failed to initialize payment."})

    return render(request, 'payment/payment_form.html', {
        'plans': SUBSCRIPTION_PLANS
    })


def payment_callback(request):
    status = request.GET.get('status')
    tx_ref = request.GET.get('tx_ref')

    if not tx_ref:
        return render(request, 'payment/payment_result.html', {'status': 'missing tx_ref'})

    try:
        payment = Payment.objects.get(tx_ref=tx_ref)
    except Payment.DoesNotExist:
        return render(request, 'payment/payment_result.html', {'status': 'invalid transaction'})

    if status != 'successful':
        payment.status = 'failed'
        payment.save()
        return render(request, 'payment/payment_result.html', {'status': 'failed'})

    # Verify payment with Flutterwave
    headers = {"Authorization": f"Bearer {settings.FLW_SECRET_KEY}"}
    verify_url = f"https://api.flutterwave.com/v3/transactions/verify_by_reference?tx_ref={tx_ref}"
    response = requests.get(verify_url, headers=headers)
    res_data = response.json()

    if res_data.get('status') != 'success' or res_data['data']['status'] != 'successful':
        payment.status = 'failed'
        payment.save()
        return render(request, 'payment/payment_result.html', {'status': 'verification failed'})

    # Mark payment as successful
    payment.status = 'successful'
    payment.save()

    plan = res_data['data']['meta'].get('plan')
    duration = int(res_data['data']['meta'].get('duration', 1))

    if plan not in SUBSCRIPTION_PLANS:
        return render(request, 'payment/payment_result.html', {'status': 'invalid plan'})

    total_days = SUBSCRIPTION_PLANS[plan]['duration_days'] * duration
    expires_at = timezone.now() + timedelta(days=total_days)

    # Activate/Update Subscription
    Subscription.objects.update_or_create(
        user=payment.user,
        defaults={
            'plan': plan,
            'started_at': timezone.now(),
            'expires_at': expires_at
        }
    )

    return render(request, 'payment/payment_result.html', {
        'status': 'success',
        'plan': plan,
        'expires_at': expires_at
    })
    
    
# launch subscription process
def get_plan_details(plan_id):
    """Helper function to get plan details"""
    for choice in Subscription.PLAN_CHOICES:
        if choice[0] == plan_id:
            return {
                'id': choice[0],
                'name': choice[1],
                'price': get_plan_price(choice[0]),
                'duration_options': [d[0] for d in Subscription.DURATION_CHOICES],
                'features': get_plan_features(choice[0])
            }
    return None

def get_plan_price(plan_id):
    """Returns the price for each plan"""
    prices = {
        Subscription.PLAN_FREE: 0,
        Subscription.PLAN_PREMIUM: 499,
        Subscription.PLAN_BUSINESS: 1999,
        Subscription.PLAN_ENTERPRISE: 4999
    }
    return prices.get(plan_id, 0)

def get_plan_features(plan_id):
    """Returns features for each plan"""
    features = {
        Subscription.PLAN_FREE: ["1 Property Listing", "Basic Support"],
        Subscription.PLAN_PREMIUM: ["10 Listings", "Featured Listings", "Email Support"],
        Subscription.PLAN_BUSINESS: ["Unlimited Listings", "Priority Support", "Analytics"],
        Subscription.PLAN_ENTERPRISE: ["All Business Features", "Dedicated Account Manager"]
    }
    return features.get(plan_id, [])

# 
def subscribe(request, plan_id):
    """Handle subscription request and render payment form"""
    if request.method == 'POST':
        try:
            duration = int(request.POST.get('duration', '30'))
            
            # Validate plan
            plan = get_plan_details(plan_id)
            if not plan:
                messages.error(request, "Invalid subscription plan")
                return redirect('home')

            # Validate duration
            if duration not in [d[0] for d in Subscription.DURATION_CHOICES]:
                duration = 30  # Default to 1 month

            # Calculate amount (monthly rate * number of months)
            amount = plan['price'] * (duration / 30)
            tax = amount * 0.16  # 16% VAT
            total = amount + tax
            
            # Store in session for payment processing
            request.session['subscription_data'] = {
                'plan_id': plan_id,
                'duration': duration,
                'amount': amount,
                'total_amount': total,
                'features': get_plan_features(plan_id)
            }
            
            # Redirect to payment page with parameters
            return redirect(reverse('make_payment') + f"?plan={plan_id}&amount={amount:.2f}&duration={duration}&total={total:.2f}")
            
        except ValueError:
            messages.error(request, "Invalid duration")
            return redirect('plans')
    
    # If not POST, redirect back
    return redirect('pricing_page')
        
        

def process_payment(request):
    """Process payment and create subscription"""
    if request.method == 'POST':
        plan_id = request.POST.get('plan_id')
        duration = int(request.POST.get('duration'))
        
        # Validate plan
        plan = get_plan_details(plan_id)
        if not plan:
            messages.error(request, "Invalid subscription plan")
            return redirect('home')

        # Validate duration
        if duration not in [d[0] for d in Subscription.DURATION_CHOICES]:
            duration = 30  # Default to 1 month

        # Calculate amount (monthly rate * number of months)
        amount = plan['price'] * (duration / 30)

        # Process payment (e.g., using Stripe API)
        # ...

        # Create subscription
        subscription = Subscription.objects.create(
            user=request.user,
            plan=plan_id,
            duration=duration,
            amount=amount
        )

        messages.success(request, "Subscription successful!")
        return redirect('home')

    return redirect('plans')
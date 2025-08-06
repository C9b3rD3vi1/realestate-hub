import uuid
import requests
from types import LambdaType
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
    
    
    
def make_payment(request):
    if request.method == 'POST':
        plan = request.POST.get('plan')  # 'premium' or 'business'
        duration = int(request.POST.get('duration', 1))  # in months

        # Example pricing (customize as needed)
        plan_prices = {
            'premium': 1000,  # KES
            'business': 2500,
        }

        amount = plan_prices.get(plan, 0) * duration
        tx_ref = str(uuid.uuid4())

        # Save the initial payment
        payment = Payment.objects.create(
            user=request.user,
            tx_ref=tx_ref,
            amount=amount,
            status='pending'
        )

        # Prepare payload for Flutterwave
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
                "description": f"{duration} Month Subscription to {plan.title()} Plan",
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

        # Request to Flutterwave
        response = requests.post(
            'https://api.flutterwave.com/v3/payments',
            json=data,
            headers=headers
        )

        if response.status_code == 200:
            payment_link = response.json()['data']['link']
            return redirect(payment_link)
        else:
            return render(request, 'payment/error.html', {"error": "Payment initiation failed."})

    return render(request, 'payment/payment_form.html')


# flutterwave payment callback and configuration
def payment_callback(request):
    status = request.GET.get('status')
    tx_ref = request.GET.get('tx_ref')

    try:
        payment = Payment.objects.get(tx_ref=tx_ref)

        if status == 'successful':
            # Confirm via Flutterwave verification
            verify_url = f"https://api.flutterwave.com/v3/transactions/verify_by_reference?tx_ref={tx_ref}"
            headers = {
                "Authorization": f"Bearer {settings.FLW_SECRET_KEY}",
            }
            response = requests.get(verify_url, headers=headers)
            res_data = response.json()

            if res_data['status'] == 'success' and res_data['data']['status'] == 'successful':
                payment.status = 'successful'
                payment.save()

                plan = res_data['data']['meta'].get('plan')
                duration = int(res_data['data']['meta'].get('duration', 1))

                expires_at = timezone.now() + timedelta(days=30 * duration)

                Subscription.objects.update_or_create(
                    user=payment.user,
                    defaults={
                        'plan': plan,
                        'started_at': timezone.now(),
                        'expires_at': expires_at
                    }
                )

        else:
            payment.status = 'failed'
            payment.save()

    except Payment.DoesNotExist:
        pass

    return render(request, 'payment/payment_result.html', {'status': status})


# subscription plans 
SUBSCRIPTION_PLANS = {
    0: {"plan": "free", "duration_days": 30},
    499: {"plan": "premium", "duration_days": 90},
    1999: {"plan": "enterprise", "duration_days": 180},
    4999: {"plan": "ultimate", "duration_days": 365},
}

def activate_subscription(request):
    status = request.GET.get('status')
    tx_ref = request.GET.get('tx_ref')

    if status != 'successful' or not tx_ref:
        return render(request, 'payment/payment_result.html', {'status': 'failed'})

    try:
        payment = Payment.objects.get(tx_ref=tx_ref, status='pending')
    except Payment.DoesNotExist:
        return render(request, 'payment/payment_result.html', {'status': 'invalid transaction'})

    # Mark payment as successful
    payment.status = 'successful'
    payment.save()

    # Determine plan from amount paid
    plan_info = SUBSCRIPTION_PLANS.get(int(payment.amount))
    if not plan_info:
        return render(request, 'payment/payment_result.html', {'status': 'unknown plan'})

    duration = timedelta(days=plan_info['duration_days'])

    # Create or update the user's subscription
    subscription, _ = Subscription.objects.get_or_create(user=payment.user)
    subscription.plan = plan_info['plan']
    subscription.started_at = timezone.now()
    subscription.expires_at = timezone.now() + duration
    subscription.save()

    return render(request, 'payment/payment_result.html', {
        'status': 'success',
        'plan': subscription.plan,
        'expires_at': subscription.expires_at
    })
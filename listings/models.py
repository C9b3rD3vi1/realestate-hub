from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.http import MAX_URL_LENGTH
from django.utils.text import slugify
from taggit.managers import TaggableManager
from django.utils.regex_helper import Choice
from django.contrib.auth.models import User, AbstractUser
from django.utils import timezone
from datetime import timedelta, datetime


#Custom User model
class CustomUser(AbstractUser):
    # This model extends the default Django User model to include additional fields
    # such as role, phone number, address, and profile picture
    ROLE_CHOICES = (
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
        ('agent', 'Agent'),
        ('admin', 'Admin'),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='buyer')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    account_status = models.CharField(max_length=15, choices=[
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('pending', 'Pending Approval'),
    ], default='active')
    bio = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # check if user is seller or agent
    def is_seller_or_agent(self):
        return self.role in ['seller', 'agent']

    def __str__(self):
        return self.username



class NeighborhoodFeature(models.Model):
    name = models.CharField(max_length=100)
    distance = models.CharField(max_length=50)
    icon = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.name} ({self.distance})"

class Amenity(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.name

# land model for real estate listings  # optional, for tagging
class LandProperties(models.Model):
    LAND_TYPE_CHOICES = [
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
        ('agricultural', 'Agricultural'),
        ('industrial', 'Industrial'),
        ('mixed_use', 'Mixed Use'),
        ('recreational', 'Recreational'),
        ('institutional', 'Institutional'),
    ]

    UNIT_CHOICES = [
        ('acres', 'Acres'),
        ('sq_ft', 'Square Feet'),
        ('hectares', 'Hectares'),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    image = models.ImageField(upload_to='land_images/')
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    location = models.CharField(max_length=255)

    size = models.DecimalField(max_digits=10, decimal_places=2)
    size_unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='acres')

    land_type = models.CharField(max_length=20, choices=LAND_TYPE_CHOICES, default='residential')

    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    neighborhood = models.ForeignKey(NeighborhoodFeature, on_delete=models.CASCADE, null=True, blank=True)

    is_available = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    amenities = models.ManyToManyField(Amenity, blank=True)

    owner = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='land_properties')

    tags = TaggableManager(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Land Properties'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('land_detail', kwargs={'slug': self.slug})

    def generate_slug(self):
        base_slug = slugify(self.title)
        slug = base_slug
        counter = 1
        while LandProperties.objects.filter(slug=slug).exclude(id=self.id).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        self.slug = slug
        return self.slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.generate_slug()
        super().save(*args, **kwargs)


# This model creates the listing for housing properties
class HousingProperties(models.Model):
    HOUSE_TYPE_CHOICES = [
        ('apartment', 'Apartment'),
        ('bungalow', 'Bungalow'),
        ('maisonette', 'Maisonette'),
        ('duplex', 'Duplex'),
        ('studio', 'Studio'),
        ('bedsitter', 'Bedsitter'),
        ('villa', 'Villa'),
        ('townhouse', 'Townhouse'),
        ('penthouse', 'Penthouse'),
        ('cottage', 'Cottage'),
        ('mansion', 'Mansion'),
        ('detached', 'Detached House'),
        ('semi_detached', 'Semi-Detached House'),
    ]

    HOUSE_SIZE_CHOICES = [
        ('studio', 'Studio'),
        ('bedsitter', 'Bedsitter'),
        ('1_bedroom', '1 Bedroom'),
        ('2_bedroom', '2 Bedroom'),
        ('3_bedroom', '3 Bedroom'),
        ('4_bedroom', '4 Bedroom'),
        ('5_bedroom', '5 Bedroom'),
        ('6_bedroom', '6 Bedroom'),
        ('7_plus_bedroom', '7+ Bedroom'),
    ]

    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='housing_images/')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    amenities = models.ManyToManyField(Amenity, related_name='houses')
    location = models.CharField(max_length=255)
    house_type = models.CharField(max_length=255, choices=HOUSE_TYPE_CHOICES, default='Apartment')
    size = models.CharField(max_length=20, choices=HOUSE_SIZE_CHOICES, default='Studio')
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)
    neighborhood = models.ManyToManyField(NeighborhoodFeature, blank=True)
    is_featured = models.BooleanField(default=False)
    is_new = models.BooleanField(default=True)
    is_sold = models.BooleanField(default=False)
    slug = models.SlugField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('housing_detail', kwargs={'slug': self.slug})

    def generate_slug(self):
        base_slug = slugify(self.title)
        slug = base_slug
        counter = 1
        while HousingProperties.objects.filter(slug=slug).exclude(id=self.id).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        self.slug = slug
        return self.slug

    def save(self, *args, **kwargs):
        self.generate_slug()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Housing Property'
        verbose_name_plural = 'Housing Properties'
        ordering = ['-created_at']


class CarProperties(models.Model):
    MAKE_CHOICES = [
        ('toyota', 'Toyota'),
        ('honda', 'Honda'),
        ('ford', 'Ford'),
        ('chevrolet', 'Chevrolet'),
        ('nissan', 'Nissan'),
        ('bmw', 'BMW'),
        ('audi', 'Audi'),
        ('mercedes', 'Mercedes-Benz'),
        ('volkswagen', 'Volkswagen'),
        ('hyundai', 'Hyundai'),
        ('kia', 'Kia'),
        ('subaru', 'Subaru'),
        ('mazda', 'Mazda'),
        ('volvo', 'Volvo'),
        ('land_rover', 'Land Rover'),
        ('jaguar', 'Jaguar'),
        ('porsche', 'Porsche'),
        ('tesla', 'Tesla'),
        ('other', 'Other'),
    ]

    MODEL_CHOICES = [
        ('corolla', 'Corolla'),
        ('civic', 'Civic'),
        ('mustang', 'Mustang'),
        ('camaro', 'Camaro'),
        ('altima', 'Altima'),
        ('3_series', '3 Series'),
        ('a4', 'A4'),
        ('c_class', 'C-Class'),
        ('golf', 'Golf'),
        ('elantra', 'Elantra'),
        ('soul', 'Soul'),
        ('forester', 'Forester'),
        ('cx_5', 'CX-5'),
        ('xc60', 'XC60'),
        ('discovery', 'Discovery'),
        ('f_type', 'F-Type'),
        ('911', '911'),
        ('model_s', 'Model S'),
        ('model_3', 'Model 3'),
        ('202', '202'),
        ('v8', 'V8'),
        ('suv', 'SUV'),
        ('pickup', 'Pickup'),
        ('sedan', 'Sedan'),
        ('hatchback', 'Hatchback'),
        ('convertible', 'Convertible'),
        ('coupe', 'Coupe'),
        ('wagon', 'Wagon'),
        ('van', 'Van'),
        ('other', 'Other'),
    ]

    FUEL_CHOICES = [
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid'),
    ]

    TRANSMISSION_CHOICES = [
        ('manual', 'Manual'),
        ('automatic', 'Automatic'),
    ]

    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='car_images/')
    description = models.TextField()

    make = models.CharField(max_length=50, choices=MAKE_CHOICES, default='toyota')
    model = models.CharField(max_length=50, choices=MODEL_CHOICES, default='corolla')
    year_of_manufacture = models.PositiveIntegerField()
    mileage = models.DecimalField(max_digits=10, decimal_places=2)  # in km
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES, default='petrol')
    engine_size = models.DecimalField(max_digits=10, decimal_places=2)  # in liters
    transmission = models.CharField(max_length=20, choices=TRANSMISSION_CHOICES, default='automatic')

    number_of_doors = models.PositiveIntegerField()
    number_of_seats = models.PositiveIntegerField()
    color = models.CharField(max_length=50)
    features = models.TextField(blank=True, null=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=255)
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    slug = models.SlugField(max_length=255, unique=True)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('car_detail', kwargs={'slug': self.slug})

    def generate_slug(self):
        base_slug = slugify(self.title)
        slug = base_slug
        counter = 1
        while CarProperties.objects.filter(slug=slug).exclude(id=self.id).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        self.slug = slug
        return self.slug

    def save(self, *args, **kwargs):
        self.generate_slug()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Car Property"
        verbose_name_plural = "Car Properties"
        ordering = ['-created_at']

 # This model stores multiple images for a car property
class CarPropertiesImage(models.Model):
    car = models.ForeignKey(CarProperties, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='car_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (self.car.title)


class HousePropertiesImage(models.Model):
    house = models.ForeignKey(HousingProperties, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='house_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (self.house.title)

class LandPropertiesImage(models.Model):
    land = models.ForeignKey(LandProperties, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='land_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (self.land.title)


# Profile model connected to CustomUser
class Profile(models.Model):
    # This model represents a user's profile, which is linked to the CustomUser model
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    favorites = models.ManyToManyField(CarProperties, related_name='favorited_by', blank=True)

    def __str__(self):
        return self.user.username



class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.name)

# User reviews and feedback messages and satisfactionns
class Testimonials(models.Model):
    name = models.CharField(max_length=100, blank=False)
    subject = models.CharField(max_length=255, blank=False)
    body = models.TextField(blank=False)

    def __str__(self):
        return str(self.name)


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


# Frequently Asked Questions
class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.question

# payment system
class Payment(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_SUCCESS = 'success'
    STATUS_FAILED = 'failed'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_SUCCESS, 'Success'),
        (STATUS_FAILED, 'Failed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tx_ref = models.CharField("Transaction Reference", max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="KES")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Payment"
        verbose_name_plural = "Payments"

    def __str__(self):
        return f"{self.user.username} | {self.tx_ref} | {self.status}"


class Subscription(models.Model):
    PLAN_FREE = 'free'
    PLAN_PREMIUM = 'premium'
    PLAN_BUSINESS = 'business'
    PLAN_ENTERPRISE = 'enterprise'

    PLAN_CHOICES = [
        (PLAN_FREE, 'Free'),
        (PLAN_PREMIUM, 'Premium'),
        (PLAN_BUSINESS, 'Business'),
        (PLAN_ENTERPRISE, 'Enterprise'),
    ]

    DURATION_CHOICES = [
        (30, '1 Month'),
        (90, '3 Months'),
        (180, '6 Months'),
        (365, '1 Year'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plan = models.CharField(
        max_length=20,
        choices=PLAN_CHOICES,
        default=PLAN_FREE
    )
    duration = models.PositiveIntegerField(
        choices=DURATION_CHOICES,
        default=30,
        help_text="Duration in days"
    )
    started_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True)
    auto_renew = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"

    def is_active(self):
        """
        Check if the subscription is currently active.
        """
        return (
            self.plan != self.PLAN_FREE and
            self.expires_at and
            self.expires_at > timezone.now()
        )

    def days_remaining(self):
        """
        Return the number of days left before expiration.
        """
        if self.expires_at:
            delta = self.expires_at - timezone.now()
            return max(delta.days, 0)
        return 0

    def activate(self, plan, duration_days):
        """
        Activate or renew a subscription based on payment.
        """
        now = timezone.now()
        self.plan = plan
        self.duration = duration_days
        self.started_at = now
        self.expires_at = now + timedelta(days=duration_days)
        self.save()

    def deactivate(self):
        """
        Revert to the free plan.
        """
        self.plan = self.PLAN_FREE
        self.duration = 0
        self.expires_at = None
        self.save()

    def __str__(self):
        status = "Active" if self.is_active() else "Expired"
        return f"{self.user.username} - {self.plan.capitalize()} ({status})"

class PropertyTestimonialLand(models.Model):
    property = models.ForeignKey(LandProperties, on_delete=models.CASCADE, related_name='testimonials')
    name = models.CharField(max_length=100)
    comment = models.TextField()
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    avatar_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Testimonial by {self.name}"

class PropertyTestimonialCar(models.Model):
    property = models.ForeignKey(CarProperties, on_delete=models.CASCADE, related_name='testimonials')
    name = models.CharField(max_length=100)
    comment = models.TextField()
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    avatar_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Testimonial by {self.name}"



class PropertyTestimonialHouse(models.Model):
    property = models.ForeignKey(HousingProperties, on_delete=models.CASCADE, related_name='testimonials')
    name = models.CharField(max_length=100)
    comment = models.TextField()
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    avatar_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Testimonial by {self.name}"



# Property History prices
class PriceHistoryLand(models.Model):
    property = models.ForeignKey(LandProperties, on_delete=models.CASCADE, related_name='price_history')
    price = models.DecimalField(max_digits=12, decimal_places=2)
    date_recorded = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.property.title} - {self.price} on {self.date_recorded}"

class PriceHistoryHouse(models.Model):
    property = models.ForeignKey(HousingProperties, on_delete=models.CASCADE, related_name='price_history')
    price = models.DecimalField(max_digits=12, decimal_places=2)
    date_recorded = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.property.title} - {self.price} on {self.date_recorded}"


class PriceHistoryCar(models.Model):
    property = models.ForeignKey(CarProperties, on_delete=models.CASCADE, related_name='price_history')
    price = models.DecimalField(max_digits=12, decimal_places=2)
    date_recorded = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.property.title} - {self.price} on {self.date_recorded}"

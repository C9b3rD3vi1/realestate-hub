from django.db import models
from django.urls import reverse
from django.utils.http import MAX_URL_LENGTH
from django.utils.text import slugify
from taggit.managers import TaggableManager
from django.utils.regex_helper import Choice
from django.contrib.auth.models import User, AbstractUser


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

    is_available = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)

    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='land_properties')

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
    location = models.CharField(max_length=255)
    house_type = models.CharField(max_length=255, choices=HOUSE_TYPE_CHOICES, default='Apartment')
    size = models.CharField(max_length=20, choices=HOUSE_SIZE_CHOICES, default='Studio')
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    #is_sold = models.BooleanField(default=False)
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
from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.urls import reverse
from django.utils.text import slugify


#Custom User model
class CustomUser(AbstractUser):
    # This model extends the default Django User model to include additional fields
    # such as role, phone number, address, and profile picture
    ROLE_CHOICES = (
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
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

    def __str__(self):
        return self.username



# Profile model connected to CustomUser
class Profile(models.Model):
    # This model represents a user's profile, which is linked to the CustomUser model
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.user.username

# land model for real estate listings
class LandProperties(models.Model):
    # This model represents a piece of land for sale or rent
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='land_images/')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=255)
    size = models.DecimalField(max_digits=10, decimal_places=2)  # Size in acres
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)
    slug = models.SlugField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    class Meta:
        verbose_name_plural = 'Land Properties'
        ordering = ['-created_at']
        
        # This method returns the URL to access a particular land property 
        # It uses the slug field to create a unique URL for each property
    def get_absolute_url(self):
        return reverse('land_detail', kwargs={'slug': self.slug})
    # This method generates a slug for the land property based on its title
    def generate_slug(self):
        # Use the slugify function to create a slug from the title
        base_slug = slugify(self.title)
        slug = base_slug
        counter = 1
        # Keep checking until we find a unique slug
        while LandProperties.objects.filter(slug=slug).exclude(id=self.id).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        self.slug = slug
        return self.slug
    # This method is called before saving the model instance to the database
    def save(self, *args, **kwargs):
        # Generate the slug before saving
        self.generate_slug()
        # Call the parent class's save method to save the instance
        super().save(*args, **kwargs)
  
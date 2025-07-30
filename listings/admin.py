from django.contrib import admin

# Register your models here.
from .models import CustomUser, Profile, LandProperties, Contact, CarProperties
from .models import HousingProperties, Testimonials, NewsletterSubscriber, CarPropertiesImage


#register your models here.
admin.site.register(CustomUser)
admin.site.register(Profile)
admin.site.register(CarProperties)
admin.site.register(HousingProperties)
admin.site.register(LandProperties)
admin.site.register(Contact)
admin.site.register(Testimonials)
admin.site.register(NewsletterSubscriber)
admin.site.register(CarPropertiesImage)

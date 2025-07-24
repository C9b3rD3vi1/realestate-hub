from django.contrib import admin

# Register your models here.
from .models import CustomUser, Profile, LandProperties, Contact, CarProperties, HousingProperties

#register your models here.
admin.site.register(CustomUser)
admin.site.register(Profile)
admin.site.register(CarProperties)
admin.site.register(HousingProperties)
admin.site.register(LandProperties)
admin.site.register(Contact)

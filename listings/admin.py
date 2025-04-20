from django.contrib import admin

# Register your models here.
from .models import CustomUser, Profile, LandProperties

#register your models here.
admin.site.register(CustomUser)
admin.site.register(Profile)
admin.site.register(LandProperties)

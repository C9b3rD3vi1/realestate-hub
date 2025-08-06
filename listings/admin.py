from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _


# Register your models here.
from .models import CustomUser
from .models import CustomUser, Profile, LandProperties, Contact, CarProperties, LandPropertiesImage, HousePropertiesImage
from .models import HousingProperties, Testimonials, NewsletterSubscriber, CarPropertiesImage, FAQ


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
admin.site.register(HousePropertiesImage)
admin.site.register(LandPropertiesImage)


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('question',)

# create custom user admin and roles 
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    
    fieldsets = (
        *(UserAdmin.fieldsets or ()),
        (_('Role info'), {'fields': ('role',)}),
    )
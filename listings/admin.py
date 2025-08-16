from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _


# Register your models here.
from .models import CustomUser, PriceHistoryHouse, PriceHistoryLand, Amenity
from .models import CustomUser, Profile, LandProperties, Contact, CarProperties, LandPropertiesImage, HousePropertiesImage
from .models import HousingProperties, Testimonials, NewsletterSubscriber, CarPropertiesImage, FAQ, Payment, Subscription
from .models import NeighborhoodFeature, PropertyTestimonialLand, PriceHistoryLand, PropertyTestimonialHouse, PropertyTestimonialCar, PriceHistoryCar

#register your models here.
admin.site.register(CustomUser)
admin.site.register(Profile)
admin.site.register(CarProperties)
admin.site.register(HousingProperties)
admin.site.register(LandProperties)
admin.site.register(Contact)
admin.site.register(Testimonials)
admin.site.register(NewsletterSubscriber)
#
admin.site.register(CarPropertiesImage)
admin.site.register(HousePropertiesImage)
admin.site.register(LandPropertiesImage)
#
admin.site.register(PriceHistoryLand)
admin.site.register(PriceHistoryHouse)
admin.site.register(PriceHistoryCar)
#
admin.site.register(NeighborhoodFeature)
#
admin.site.register(PropertyTestimonialLand)
admin.site.register(PropertyTestimonialHouse)
admin.site.register(PropertyTestimonialCar)
admin.site.register(Amenity)
#admin.site.register(Payment)


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
    
admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "started_at", "expires_at", "is_active")
    list_filter = ("plan", "started_at", "expires_at")

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("user", "tx_ref", "amount", "status", "created_at")
    list_filter = ("status", "currency", "created_at")
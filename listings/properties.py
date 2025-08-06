from types import LambdaType
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import LandPropertyForm, HousingPropertyForm, CarPropertyForm
from .decorators import seller_or_agent_required



@login_required
#@seller_or_agent_required
def add_property(request):
    property_type = request.POST.get('property_type') or request.GET.get('property_type', '')

    form_classes = {
        'land': LandPropertyForm,
        'house': HousingPropertyForm,
        'car': CarPropertyForm,
    }

    selected_form_class = form_classes.get(property_type)

    form = selected_form_class(request.POST or None, request.FILES or None) if selected_form_class else None

    if request.method == 'POST' and form:
        if form.is_valid():
            property_obj = form.save(commit=False)
            property_obj.posted_by = request.user
            property_obj.save()
            return redirect('property_list')

    context = {
        'form': form,
        'property_type': property_type,
        'land_form': LandPropertyForm(),
        'house_form': HousingPropertyForm(),
        'car_form': CarPropertyForm(),
    }

    return render(request, 'components/addproperty.html', context) 
